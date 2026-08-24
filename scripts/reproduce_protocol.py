#!/usr/bin/env python3
"""Reproducibility runner for the TCSA governance-aware XAI manuscript.

This public script reproduces the leakage-aware CICIDS2017-derived sample
protocol used in the manuscript: duplicate control, exact-feature-group-aware
holdout, calibrated RF/GB/LR baselines, bootstrap intervals, a CV sanity check,
SHAP-based global/local evidence when available, original-label outcomes, and
illustrative risk-priority examples.
"""
from __future__ import annotations

import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.frozen import FrozenEstimator
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, average_precision_score,
    balanced_accuracy_score, brier_score_loss, confusion_matrix, f1_score,
    precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

try:
    import shap
except Exception:
    shap = None


def norm(s: str) -> str:
    return str(s).strip().replace(" ", "_").replace("/", "_per_")


def binary_labels(y: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(y):
        return (pd.to_numeric(y, errors="coerce").fillna(0) != 0).astype(int)
    benign = {"BENIGN", "NORMAL", "0", "FALSE", "LEGITIMATE"}
    return y.astype(str).str.strip().str.upper().map(lambda v: 0 if v in benign else 1).astype(int)


def clean(df: pd.DataFrame, label: str):
    df = df.copy(); df.columns = [norm(c) for c in df.columns]; label = norm(label)
    if label not in df: raise SystemExit(f"Label column {label!r} not found")
    y0 = df[label].astype(str); x = df.drop(columns=[label]).dropna(axis=1, how="all")
    raw_features = x.shape[1]; x = x.replace([np.inf, -np.inf], np.nan)
    constant = [c for c in x if x[c].nunique(dropna=True) <= 1]
    x = x.drop(columns=constant)
    return x, y0, {"raw_feature_count": int(raw_features), "features_after_cleaning": int(x.shape[1]),
                   "constant_or_uninformative_columns_removed": constant}


def dup_meta(x, y, y0):
    h = pd.util.hash_pandas_object(x, index=False)
    counts = h.value_counts()
    t = pd.DataFrame({"h": h, "y": y.values, "l": y0.astype(str).values})
    e = x.copy(); e["__label__"] = y0.astype(str).values
    return {"exact_duplicate_feature_label_rows": int(e.duplicated().sum()),
            "feature_duplicate_groups": int((counts > 1).sum()),
            "conflicting_feature_binary_label_groups": int((t.groupby("h")["y"].nunique() > 1).sum()),
            "conflicting_feature_original_label_groups": int((t.groupby("h")["l"].nunique() > 1).sum())}


def dedupe(x, y, y0):
    e = x.copy(); e["__label__"] = y0.astype(str).values
    keep = ~e.duplicated(keep="first")
    return (x.loc[keep].reset_index(drop=True), y.loc[keep].reset_index(drop=True),
            y0.loc[keep].reset_index(drop=True), int((~keep).sum()))


def group_split(x, y, y0, test_size=.25, seed=42):
    groups = pd.util.hash_pandas_object(x, index=False).astype(str)
    n = max(2, int(round(1 / test_size)))
    sgkf = StratifiedGroupKFold(n_splits=n, shuffle=True, random_state=seed)
    target = float(y.mean())
    candidates = list(sgkf.split(x, y, groups))
    def score(pair):
        _, te = pair
        return abs(len(te)/len(x)-test_size) + abs(float(y.iloc[te].mean())-target)
    tr, te = min(candidates, key=score)
    xt, xv = x.iloc[tr].reset_index(drop=True), x.iloc[te].reset_index(drop=True)
    yt, yv = y.iloc[tr].reset_index(drop=True), y.iloc[te].reset_index(drop=True)
    ltr, lv = y0.iloc[tr].reset_index(drop=True), y0.iloc[te].reset_index(drop=True)
    ht = set(pd.util.hash_pandas_object(xt, index=False).tolist())
    overlap = int(pd.util.hash_pandas_object(xv, index=False).isin(ht).sum())
    return xt, xv, yt, yv, ltr, lv, {"split_method": f"stratified_group_kfold_holdout_{n}_folds",
        "train_test_exact_feature_overlap_rows": overlap, "train_rows":len(xt), "test_rows":len(xv)}


def preprocessor(x):
    num = [c for c in x if pd.api.types.is_numeric_dtype(x[c])]; cat = [c for c in x if c not in num]
    return ColumnTransformer([
        ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), num),
        ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                          ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), cat)
    ], remainder="drop", verbose_feature_names_out=False)


def models(seed=42):
    return {"Random Forest": RandomForestClassifier(n_estimators=100, random_state=seed, n_jobs=-1, class_weight="balanced"),
            "Gradient Boosting": GradientBoostingClassifier(random_state=seed),
            "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced")}


def fit_calibrated(model, x, y, seed=42):
    xf, xc, yf, yc = train_test_split(x, y, test_size=.20, random_state=seed, stratify=y)
    base = Pipeline([("preprocess", preprocessor(x)), ("model", model)]).fit(xf, yf)
    cal = CalibratedClassifierCV(FrozenEstimator(base), method="sigmoid").fit(xc, yc)
    return cal, base, "sigmoid_holdout_0.20"


def scores(est, x):
    if hasattr(est, "predict_proba"): return np.asarray(est.predict_proba(x))[:,1]
    raw = np.asarray(est.decision_function(x)); return 1/(1+np.exp(-raw))


def boot_ci(y, p, s, metric, seed, n=300):
    rng=np.random.default_rng(seed); vals=[]; N=len(y)
    for _ in range(n):
        i=rng.integers(0,N,N); yy=y[i]
        if len(np.unique(yy))<2: continue
        vals.append(f1_score(yy,p[i],zero_division=0) if metric=="f1" else roc_auc_score(yy,s[i]))
    return tuple(np.percentile(vals,[2.5,97.5])) if vals else (np.nan,np.nan)


def evaluate(name, est, x, y, seed=42, boot=300):
    yp=np.asarray(est.predict(x),dtype=int); ys=scores(est,x); tn,fp,fn,tp=confusion_matrix(y,yp,labels=[0,1]).ravel()
    fl,fh=boot_ci(y.to_numpy(),yp,ys,"f1",seed,boot); al,ah=boot_ci(y.to_numpy(),yp,ys,"auc",seed+1,boot)
    return dict(model=name, calibration="sigmoid_holdout_0.20", accuracy=accuracy_score(y,yp),
        balanced_accuracy=balanced_accuracy_score(y,yp), precision=precision_score(y,yp,zero_division=0),
        recall=recall_score(y,yp,zero_division=0), f1=f1_score(y,yp,zero_division=0),
        f1_ci_low=fl,f1_ci_high=fh,roc_auc=roc_auc_score(y,ys),roc_auc_ci_low=al,roc_auc_ci_high=ah,
        pr_auc=average_precision_score(y,ys),brier=brier_score_loss(y,ys),
        false_positive_rate=fp/(fp+tn),false_negative_rate=fn/(fn+tp),tn=int(tn),fp=int(fp),fn=int(fn),tp=int(tp))


def per_label(est, x, y0):
    pred=np.asarray(est.predict(x),dtype=int); rows=[]
    for lab in sorted(y0.unique(), key=lambda v:(str(v).upper()!="BENIGN",str(v))):
        m=(y0==lab).to_numpy(); benign=str(lab).upper()=="BENIGN"; good=int(((pred==0 if benign else pred==1)&m).sum())
        support=int(m.sum()); rows.append(dict(class_label=lab,support=support,correct_or_detected=good,
            missed_or_false_alarm=support-good,rate_name="specificity" if benign else "attack_detection_rate",rate=good/support))
    return pd.DataFrame(rows)


def explain(base, x_test, y_test, seed=42, n=1000, use_shap=True):
    pp=base.named_steps["preprocess"]; model=base.named_steps["model"]
    rng=np.random.default_rng(seed); idx=rng.choice(len(x_test), size=min(n,len(x_test)), replace=False)
    z=pp.transform(x_test.iloc[idx]); names=list(pp.get_feature_names_out())
    if use_shap and shap is not None and hasattr(model,"estimators_"):
        try:
            arr=np.asarray(shap.TreeExplainer(model).shap_values(z))
            if arr.ndim==3: arr=arr[:,:,1]
            if arr.ndim==2 and arr.shape[1]==len(names):
                imp=np.abs(arr).mean(0); return pd.DataFrame({"feature":names,"importance":imp}).sort_values("importance",ascending=False), "mean_absolute_shap"
        except Exception: pass
    imp=np.asarray(getattr(model,"feature_importances_",np.zeros(len(names))))
    return pd.DataFrame({"feature":names,"importance":imp}).sort_values("importance",ascending=False), "model_feature_importance"


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--input",required=True); ap.add_argument("--label",default="Label")
    ap.add_argument("--output-dir",default="outputs"); ap.add_argument("--use-shap",action="store_true")
    ap.add_argument("--cv-folds",type=int,default=3); ap.add_argument("--bootstrap-iterations",type=int,default=300)
    ap.add_argument("--shap-sample-size",type=int,default=1000); ap.add_argument("--random-seed",type=int,default=42)
    ap.add_argument("--preflight-only",action="store_true",help="Validate cleaning/split counts without fitting models")
    a=ap.parse_args(); out=Path(a.output_dir); out.mkdir(parents=True,exist_ok=True)
    raw=pd.read_csv(a.input,low_memory=False); x,y0,meta=clean(raw,a.label); y=binary_labels(y0); before=dup_meta(x,y,y0)
    x,y,y0,removed=dedupe(x,y,y0); after=dup_meta(x,y,y0); xt,xv,yt,yv,lt,lv,sm=group_split(x,y,y0,seed=a.random_seed)
    split=pd.DataFrame([{"split":"train","benign":int((yt==0).sum()),"attack":int((yt==1).sum()),"total":len(yt),"positive_rate":float(yt.mean())},
                        {"split":"test","benign":int((yv==0).sum()),"attack":int((yv==1).sum()),"total":len(yv),"positive_rate":float(yv.mean())}])
    split.to_csv(out/"train_test_distribution.csv",index=False)
    if a.preflight_only:
        report={"n_rows_loaded":len(raw),"n_rows_used":len(x),"exact_duplicate_rows_removed":removed,**meta,**before,**after,**sm}
        (out/"preflight.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
        print(json.dumps(report,indent=2)); return
    cd=y0.value_counts().rename_axis("class_label").reset_index(name="count"); cd["percentage"]=cd["count"]/cd["count"].sum()*100; cd.to_csv(out/"class_distribution.csv",index=False)
    result=[]; cv=[]; fitted={}; bases={}
    for name,m in models(a.random_seed).items():
        est,base,_=fit_calibrated(m,xt,yt,a.random_seed); result.append(evaluate(name,est,xv,yv,a.random_seed,a.bootstrap_iterations)); fitted[name]=est; bases[name]=base
        if a.cv_folds>=2:
            pipe=Pipeline([("preprocess",preprocessor(x)),("model",m)])
            sc=cross_val_score(pipe,x,y,cv=StratifiedKFold(a.cv_folds,shuffle=True,random_state=a.random_seed),scoring="f1",n_jobs=1)
            cv.append({"model":name,"cv_f1_mean":float(sc.mean()),"cv_f1_std":float(sc.std())})
    md=pd.DataFrame(result).sort_values(["f1","roc_auc","brier"],ascending=[False,False,True]).reset_index(drop=True); md.to_csv(out/"model_metrics.csv",index=False)
    if cv: pd.DataFrame(cv).to_csv(out/"cv_metrics.csv",index=False)
    pd.DataFrame([{k:r[k] for k in ["model","tn","fp","fn","tp"]} for _,r in md.iterrows()]).to_csv(out/"confusion_matrices.csv",index=False)
    best=str(md.iloc[0].model); per_label(fitted[best],xv,lv).to_csv(out/"per_label_detection.csv",index=False)
    fi,method=explain(bases[best],xv,yv,a.random_seed,a.shap_sample_size,a.use_shap); fi.to_csv(out/"feature_importance.csv",index=False)
    removed_df=pd.DataFrame([
      ["Raw numeric/flow features",meta["raw_feature_count"]],["Features after cleaning",meta["features_after_cleaning"]],
      ["Removed constant/uninformative",", ".join(meta["constant_or_uninformative_columns_removed"])],
      ["Exact duplicate feature/label rows removed before split",removed],["Feature-vector duplicate groups after duplicate control",after["feature_duplicate_groups"]],
      ["Train-test exact feature overlap rows",sm["train_test_exact_feature_overlap_rows"]]],columns=["category","columns"])
    removed_df.to_csv(out/"removed_columns.csv",index=False)
    metadata={"input":a.input,"label":a.label,"output_dir":a.output_dir,"test_size":.25,"random_seed":a.random_seed,
      "cv_folds":a.cv_folds,"explanation_method":method,"use_shap":a.use_shap,"shap_sample_size":a.shap_sample_size,
      "calibration_size":.20,"calibration_method":"sigmoid","bootstrap_iterations":a.bootstrap_iterations,**meta,
      **{f"before_duplicate_control_{k}":v for k,v in before.items()},**{f"after_duplicate_control_{k}":v for k,v in after.items()},**sm,
      "exact_duplicate_rows_removed":removed,"n_rows_loaded":len(raw),"n_rows_used":len(x),"positive_rate":float(y.mean()),"best_model_by_f1":best,
      "research_integrity_note":"Public-sample results are leakage-aware but are not full official CICIDS2017 benchmark claims."}
    (out/"run_metadata.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
    print(f"Loaded={len(raw):,}; used={len(x):,}; duplicates_removed={removed:,}; overlap={sm['train_test_exact_feature_overlap_rows']}")
    print(f"Best model: {best}; F1={md.iloc[0].f1:.6f}; ROC-AUC={md.iloc[0].roc_auc:.6f}; method={method}")

if __name__=="__main__": main()
