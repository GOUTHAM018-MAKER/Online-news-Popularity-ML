"""Rebuild every reported result. Run from repository root; see README."""
from pathlib import Path
import argparse, zipfile, hashlib, json, platform
import numpy as np
import pandas as pd
import sklearn
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.base import clone
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
def run(source):
    out=ROOT/'results'; assets=ROOT/'docs/assets'
    out.mkdir(exist_ok=True); assets.mkdir(exist_ok=True)
    source=Path(source)
    if source.suffix=='.zip':
        with zipfile.ZipFile(source) as z: raw=z.read('OnlineNewsPopularity/OnlineNewsPopularity.csv')
    else: raw=source.read_bytes()
    import io
    df=pd.read_csv(io.BytesIO(raw)); df.columns=df.columns.str.strip(); df.insert(0,'row_id',np.arange(len(df)))
    df['date']=pd.to_datetime(df.url.str.extract(r'/(\d{4}/\d{2}/\d{2})/')[0],format='%Y/%m/%d',errors='raise')
    assert df.url.is_unique and df.shares.ge(0).all()
    # Date boundaries depend only on publication dates, never outcomes.
    dates=np.sort(df.date.unique()); b1=dates[int(.6*len(dates))]; b2=dates[int(.8*len(dates))]
    df['split']=np.where(df.date<b1,'train',np.where(df.date<b2,'validation','test'))
    excluded=[c for c in df if c.startswith(('kw_','self_reference_','LDA_'))]+['url','timedelta','shares','row_id','date','split']
    features=[c for c in df if c not in excluded]
    X=df[features].copy(); ratios=['n_unique_tokens','n_non_stop_words','n_non_stop_unique_tokens']
    invalid={c:int(((X[c]<0)|(X[c]>1)).sum()) for c in ratios}
    for c in ratios: X.loc[(X[c]<0)|(X[c]>1),c]=np.nan
    X=X.replace([np.inf,-np.inf],np.nan)
    masks={k:df.split.eq(k) for k in ['train','validation','test']}
    y=np.log1p(df.shares.to_numpy())
    configs=[('Median baseline',{}),('Ridge',{'alpha':1}),('Ridge',{'alpha':100}),('Random forest',{'min_samples_leaf':10}),('Random forest',{'min_samples_leaf':30}),('Boosted trees',{'max_leaf_nodes':15}),('Boosted trees',{'max_leaf_nodes':31})]
    def model(name,p):
        if name=='Median baseline': est=DummyRegressor(strategy='median')
        elif name=='Ridge': est=Ridge(**p)
        elif name=='Random forest': est=RandomForestRegressor(n_estimators=150,max_features=.8,n_jobs=2,random_state=335,**p)
        else: est=HistGradientBoostingRegressor(max_iter=150,learning_rate=.05,l2_regularization=10,early_stopping=False,random_state=335,**p)
        return make_pipeline(SimpleImputer(strategy='median'),StandardScaler(),est) if name=='Ridge' else make_pipeline(SimpleImputer(strategy='median'),est)
    trials=[]; best={}
    for name,p in configs:
        m=model(name,p); m.fit(X[masks['train']],y[masks['train']]); pred=m.predict(X[masks['validation']]); score=mean_absolute_error(y[masks['validation']],pred)
        trials.append({'model':name,'parameters':p,'validation_log_mae':float(score)})
        if name not in best or score<best[name][0]: best[name]=(score,p)
        print(name,p,score,flush=True)
    winner=min(best,key=lambda n:best[n][0]); test=masks['test']; fit=~test
    metrics=[]; predictions=df.loc[test,['row_id','date','shares']].copy(); predictions['channel']='Other / unlabelled'
    for c in df.columns:
        if c.startswith('data_channel_is_'): predictions.loc[df.loc[test,c].eq(1),'channel']=c.replace('data_channel_is_','')
    models={}
    for name,(score,p) in best.items():
        m=model(name,p); m.fit(X[fit],y[fit]); logpred=np.maximum(0,m.predict(X[test])); pred=np.expm1(logpred)
        models[name]=m; predictions[name]=pred
        metrics.append({'model':name,'validation_log_mae':float(score),'test_log_mae':float(mean_absolute_error(y[test],logpred)),'test_rmsle':float(np.sqrt(mean_squared_error(y[test],logpred))),'test_mae_shares':float(mean_absolute_error(df.loc[test,'shares'],pred)),'test_r2_log':float(r2_score(y[test],logpred)),'parameters':p})
    # Paired day bootstrap, after model selection; diagnostic uncertainty only.
    diff=np.abs(y[test]-np.log1p(predictions['Median baseline']))-np.abs(y[test]-np.log1p(predictions[winner]))
    day=pd.DataFrame({'date':predictions.date,'diff':diff}).groupby('date')['diff'].agg(['sum','count'])
    rng=np.random.default_rng(335); boot=[]
    for _ in range(2000):
        d=day.iloc[rng.integers(0,len(day),len(day))]; boot.append(d['sum'].sum()/d['count'].sum())
    predictions['abs_log_error']=np.abs(y[test]-np.log1p(predictions[winner]))
    groups=[]
    for label,mask in [('Under 1,000',predictions.shares<1000),('1,000–9,999',predictions.shares.between(1000,9999)),('10,000+',predictions.shares>=10000)]:
        q=predictions[mask]; groups.append({'group':label,'n':len(q),'log_mae':float(q.abs_log_error.mean()),'mae_shares':float(np.abs(q.shares-q[winner]).mean()),'median_actual':float(q.shares.median()),'median_prediction':float(q[winner].median())})
    summary={'rows':len(df),'columns':61,'features':features,'excluded':excluded,'csv_sha256':hashlib.sha256(raw).hexdigest(),'invalid_ratios':invalid,'missing_original':int(df.drop(columns=['date','split']).isna().sum().sum()),'zero_content':int(df.n_tokens_content.eq(0).sum()),'share_quantiles':{str(k):float(v) for k,v in df.shares.quantile([0,.5,.9,.99,1]).items()},'splits':{k:{'n':int(v.sum()),'start':str(df.loc[v,'date'].min().date()),'end':str(df.loc[v,'date'].max().date())} for k,v in masks.items()},'winner':winner,'metrics':metrics,'trials':trials,'error_groups':groups,'paired_day_bootstrap_95_log_mae_improvement':np.quantile(boot,[.025,.975]).tolist(),'environment':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scikit-learn':sklearn.__version__}}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)); pd.DataFrame(trials).to_json(out/'validation_trials.json',orient='records',indent=2)
    pd.DataFrame(metrics).to_csv(out/'metrics.csv',index=False); predictions.to_csv(out/'test_predictions.csv',index=False); df[['row_id','date','split']].to_csv(out/'splits.csv',index=False)
    predictions.nlargest(8,'abs_log_error').to_csv(out/'largest_errors.csv',index=False)
    (out/'feature_manifest.json').write_text(json.dumps({'included':features,'excluded':excluded},indent=2))
    # Browser data is precomputed, no model trained or uploaded by the website.
    public={'summary':summary,'predictions':json.loads(predictions.assign(date=predictions.date.dt.strftime('%Y-%m-%d')).to_json(orient='records'))}
    (assets/'results.js').write_text('window.PROJECT_DATA = '+json.dumps(public)+';\n')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white','axes.labelcolor':'#334155'})
    fig,ax=plt.subplots(figsize=(10,3.6)); ax.hist(np.log10(df.shares+1),bins=60,color='#28615b'); ax.set(xlabel='log₁₀(1 + observed shares)',ylabel='Number of articles',title='Most articles are modest. A few dominate the share counts.'); fig.tight_layout(); fig.savefig(assets/'distribution.svg'); plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,3.8)); names=[r['model'] for r in metrics]; ax.barh(names,[r['test_log_mae'] for r in metrics],color=['#becbc9' if n!=winner else '#28615b' for n in names]); ax.set(xlabel='Test mean absolute error in log(1 + shares) · lower is better',title='A chronological test, compared with a constant prediction'); fig.tight_layout(); fig.savefig(assets/'comparison.svg'); plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,4.5)); ax.hexbin(np.log10(predictions.shares+1),np.log10(predictions[winner]+1),gridsize=45,mincnt=1,cmap='Greens'); ax.plot([0,6],[0,6],color='#b45309',ls='--'); ax.set(xlabel='log₁₀(1 + observed shares)',ylabel='log₁₀(1 + predicted shares)',title='The viral tail remains hard to predict'); fig.tight_layout(); fig.savefig(assets/'errors.svg'); plt.close(fig)
    return summary
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--data',default='data/online+news+popularity.zip'); run(p.parse_args().data)
