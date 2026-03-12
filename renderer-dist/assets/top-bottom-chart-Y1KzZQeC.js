import{r as S,R as I}from"./plotly-core-CJ9sSumU.js";var te={exports:{}},U={};/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var le=S,de=Symbol.for("react.element"),ue=Symbol.for("react.fragment"),pe=Object.prototype.hasOwnProperty,he=le.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner,fe={key:!0,ref:!0,__self:!0,__source:!0};function re(e,t,r){var l,o={},n=null,f=null;r!==void 0&&(n=""+r),t.key!==void 0&&(n=""+t.key),t.ref!==void 0&&(f=t.ref);for(l in t)pe.call(t,l)&&!fe.hasOwnProperty(l)&&(o[l]=t[l]);if(e&&e.defaultProps)for(l in t=e.defaultProps,t)o[l]===void 0&&(o[l]=t[l]);return{$$typeof:de,type:e,key:n,ref:f,props:o,_owner:he.current}}U.Fragment=ue;U.jsx=re;U.jsxs=re;te.exports=U;var d=te.exports;const ge=(e,t,r,l)=>{var n,f,m,u;const o=[r,{code:t,...l||{}}];if((f=(n=e==null?void 0:e.services)==null?void 0:n.logger)!=null&&f.forward)return e.services.logger.forward(o,"warn","react-i18next::",!0);z(o[0])&&(o[0]=`react-i18next:: ${o[0]}`),(u=(m=e==null?void 0:e.services)==null?void 0:m.logger)!=null&&u.warn?e.services.logger.warn(...o):console!=null&&console.warn&&console.warn(...o)},V={},W=(e,t,r,l)=>{z(r)&&V[r]||(z(r)&&(V[r]=new Date),ge(e,t,r,l))},ne=(e,t)=>()=>{if(e.isInitialized)t();else{const r=()=>{setTimeout(()=>{e.off("initialized",r)},0),t()};e.on("initialized",r)}},H=(e,t,r)=>{e.loadNamespaces(t,ne(e,r))},X=(e,t,r,l)=>{if(z(r)&&(r=[r]),e.options.preload&&e.options.preload.indexOf(t)>-1)return H(e,r,l);r.forEach(o=>{e.options.ns.indexOf(o)<0&&e.options.ns.push(o)}),e.loadLanguages(t,ne(e,l))},xe=(e,t,r={})=>!t.languages||!t.languages.length?(W(t,"NO_LANGUAGES","i18n.languages were undefined or empty",{languages:t.languages}),!0):t.hasLoadedNamespace(e,{lng:r.lng,precheck:(l,o)=>{if(r.bindI18n&&r.bindI18n.indexOf("languageChanging")>-1&&l.services.backendConnector.backend&&l.isLanguageChangingTo&&!o(l.isLanguageChangingTo,e))return!1}}),z=e=>typeof e=="string",me=e=>typeof e=="object"&&e!==null,ye=/&(?:amp|#38|lt|#60|gt|#62|apos|#39|quot|#34|nbsp|#160|copy|#169|reg|#174|hellip|#8230|#x2F|#47);/g,be={"&amp;":"&","&#38;":"&","&lt;":"<","&#60;":"<","&gt;":">","&#62;":">","&apos;":"'","&#39;":"'","&quot;":'"',"&#34;":'"',"&nbsp;":" ","&#160;":" ","&copy;":"©","&#169;":"©","&reg;":"®","&#174;":"®","&hellip;":"…","&#8230;":"…","&#x2F;":"/","&#47;":"/"},we=e=>be[e],ke=e=>e.replace(ye,we);let K={bindI18n:"languageChanged",bindI18nStore:"",transEmptyNodeValue:"",transSupportBasicHtmlNodes:!0,transWrapTextNodes:"",transKeepBasicHtmlNodesFor:["br","strong","i","p"],useSuspense:!0,unescape:ke};const Ce=(e={})=>{K={...K,...e}},ve=()=>K;let oe;const Ne=e=>{oe=e},je=()=>oe,Ue={type:"3rdParty",init(e){Ce(e.options.react),Ne(e)}},Te=S.createContext();class Ee{constructor(){this.usedNamespaces={}}addUsedNamespaces(t){t.forEach(r=>{this.usedNamespaces[r]||(this.usedNamespaces[r]=!0)})}getUsedNamespaces(){return Object.keys(this.usedNamespaces)}}const Me=(e,t)=>{const r=S.useRef();return S.useEffect(()=>{r.current=e},[e,t]),r.current},ae=(e,t,r,l)=>e.getFixedT(t,r,l),Pe=(e,t,r,l)=>S.useCallback(ae(e,t,r,l),[e,t,r,l]),Se=(e,t={})=>{var L,O,_,R;const{i18n:r}=t,{i18n:l,defaultNS:o}=S.useContext(Te)||{},n=r||l||je();if(n&&!n.reportNamespaces&&(n.reportNamespaces=new Ee),!n){W(n,"NO_I18NEXT_INSTANCE","useTranslation: You will need to pass in an i18next instance by using initReactI18next");const y=(T,x)=>z(x)?x:me(x)&&z(x.defaultValue)?x.defaultValue:Array.isArray(T)?T[T.length-1]:T,j=[y,{},!1];return j.t=y,j.i18n={},j.ready=!1,j}(L=n.options.react)!=null&&L.wait&&W(n,"DEPRECATED_OPTION","useTranslation: It seems you are still using the old wait option, you may migrate to the new useSuspense behaviour.");const f={...ve(),...n.options.react,...t},{useSuspense:m,keyPrefix:u}=f;let h=o||((O=n.options)==null?void 0:O.defaultNS);h=z(h)?[h]:h||["translation"],(R=(_=n.reportNamespaces).addUsedNamespaces)==null||R.call(_,h);const s=(n.isInitialized||n.initializedStoreOnce)&&h.every(y=>xe(y,n,f)),w=Pe(n,t.lng||null,f.nsMode==="fallback"?h:h[0],u),M=()=>w,v=()=>ae(n,t.lng||null,f.nsMode==="fallback"?h:h[0],u),[N,P]=S.useState(M);let k=h.join();t.lng&&(k=`${t.lng}${k}`);const C=Me(k),b=S.useRef(!0);S.useEffect(()=>{const{bindI18n:y,bindI18nStore:j}=f;b.current=!0,!s&&!m&&(t.lng?X(n,t.lng,h,()=>{b.current&&P(v)}):H(n,h,()=>{b.current&&P(v)})),s&&C&&C!==k&&b.current&&P(v);const T=()=>{b.current&&P(v)};return y&&(n==null||n.on(y,T)),j&&(n==null||n.store.on(j,T)),()=>{b.current=!1,n&&y&&(y==null||y.split(" ").forEach(x=>n.off(x,T))),j&&n&&j.split(" ").forEach(x=>n.store.off(x,T))}},[n,k]),S.useEffect(()=>{b.current&&s&&P(M)},[n,u,s]);const i=[N,n,s];if(i.t=N,i.i18n=n,i.ready=s,s||!s&&!m)return i;throw new Promise(y=>{t.lng?X(n,t.lng,h,()=>y()):H(n,h,()=>y())})},G={},_e=((G==null?void 0:G.VITE_API_URL)??"").trim(),B=(_e||"/api").replace(/\/$/,"");function Ie(){var e;return typeof window<"u"&&((e=window.location)!=null&&e.origin)?window.location.origin:"http://localhost"}function Re(e){const t=e.startsWith("/")?e:`/${e}`;return/^https?:\/\//.test(B)?`${B}${t}`:new URL(`${B}${t}`,Ie()).toString()}const g={background:"#131722",gridColor:"#2a2e39",textColor:"#d1d4dc",upColor:"#26a69a",downColor:"#ef5350",sma20Color:"#00bcd4",sma50Color:"#ffeb3b",sma200Color:"#e91e63",volumeUpColor:"rgba(38, 166, 154, 0.5)",volumeDownColor:"rgba(239, 83, 80, 0.5)",entryMarkerColor:"#26a69a",exitMarkerColor:"#ef5350"};function $e(e,t){const r=[];r.push({type:"candlestick",x:e.dates,open:e.open,high:e.high,low:e.low,close:e.close,increasing:{line:{color:g.upColor}},decreasing:{line:{color:g.downColor}},name:"Price",xaxis:"x",yaxis:"y"});const l=e.close.map((o,n)=>n===0||o>=e.close[n-1]?g.volumeUpColor:g.volumeDownColor);return r.push({type:"bar",x:e.dates,y:e.volume,marker:{color:l},name:"Volume",xaxis:"x",yaxis:"y2"}),e.sma20&&r.push({type:"scatter",mode:"lines",x:e.dates,y:e.sma20,line:{color:g.sma20Color,width:1},name:"SMA 20",xaxis:"x",yaxis:"y"}),e.sma50&&r.push({type:"scatter",mode:"lines",x:e.dates,y:e.sma50,line:{color:g.sma50Color,width:1},name:"SMA 50",xaxis:"x",yaxis:"y"}),e.sma200&&r.push({type:"scatter",mode:"lines",x:e.dates,y:e.sma200,line:{color:g.sma200Color,width:1},name:"SMA 200",xaxis:"x",yaxis:"y"}),t&&(t.entries.length>0&&r.push({type:"scatter",mode:"markers",x:t.entries.map(o=>o.date),y:t.entries.map(o=>o.price),marker:{symbol:"triangle-up",size:14,color:g.entryMarkerColor},name:"Entry",xaxis:"x",yaxis:"y",text:t.entries.map(o=>`Entry: $${o.price.toFixed(2)}`),hoverinfo:"text+x"}),t.exits.length>0&&r.push({type:"scatter",mode:"markers",x:t.exits.map(o=>o.date),y:t.exits.map(o=>o.price),marker:{symbol:"triangle-down",size:14,color:g.exitMarkerColor},name:"Exit",xaxis:"x",yaxis:"y",text:t.exits.map(o=>`Exit: $${o.price.toFixed(2)}${o.pnl!==void 0?` (P&L: $${o.pnl.toFixed(2)})`:""}`),hoverinfo:"text+x"})),r}function ze(e,t,r){return{title:{text:e,font:{color:g.textColor,size:16}},paper_bgcolor:g.background,plot_bgcolor:g.background,font:{color:g.textColor},xaxis:{gridcolor:g.gridColor,rangeslider:{visible:!1},type:"date"},yaxis:{gridcolor:g.gridColor,side:"right",domain:[.3,1],title:"Price"},yaxis2:{gridcolor:g.gridColor,domain:[0,.25],title:"Volume"},width:t||1200,height:r||700,showlegend:!0,legend:{bgcolor:"rgba(19, 23, 34, 0.8)",font:{color:g.textColor}},dragmode:"pan"}}function Y({ticker:e,data:t,markers:r,width:l,height:o}){var M,v;const n=$e(t,r),f=ze(e,l,o),[m,u]=I.useState(null),h=I.useCallback(async()=>{if(!(typeof window>"u"))try{const N=await fetch(Re("/backtest/latest"));if(!N.ok)return;const P=await N.json(),k=P&&P.charts||{},C=Object.keys(k||{});let b=C.find(i=>i===`${e}_price_chart`)||C.find(i=>i===e)||C.find(i=>i.includes(e))||C.find(i=>i.includes("_price_chart"));!b&&C.length>0&&(b=C[0]),b&&k[b]&&u(k[b])}catch(N){console.warn("Failed to fetch chart preview",N)}},[e]);I.useEffect(()=>{try{h()}catch(N){console.warn("fetchChartPreview failed",N)}},[h]);let s=f;return I.useEffect(()=>{let N=!1;async function P(){try{if(m||typeof document>"u"||typeof navigator<"u"&&navigator.userAgent.includes("jsdom"))return;const k=document.createElement("canvas"),C=1200,b=700;k.width=C,k.height=b;const i=k.getContext("2d");if(!i)return;i.fillStyle=g.background,i.fillRect(0,0,C,b),i.strokeStyle=g.gridColor,i.lineWidth=1;const L=6,O=6;for(let a=1;a<L;a++){const c=Math.round(C*a/L);i.beginPath(),i.moveTo(c,0),i.lineTo(c,b),i.stroke()}for(let a=1;a<O;a++){const c=Math.round(b*a/O);i.beginPath(),i.moveTo(0,c),i.lineTo(C,c),i.stroke()}i.fillStyle=g.textColor,i.font="16px sans-serif",i.fillText(e,12,24);const _=(n||[]).find(a=>a&&(a.name==="Entry"||a.name==="Exit"));let R=[],y=[];if(_){const a=_.x||[],c=_.y||[];for(let p=0;p<a.length;p++)_.marker&&_.marker.symbol==="triangle-up"||_.name==="Entry"?R.push({x:a[p],y:c[p]}):y.push({x:a[p],y:c[p]})}const j=(n||[]).find(a=>a&&a.name==="Entry"),T=(n||[]).find(a=>a&&a.name==="Exit");if(j){const a=j.x||[],c=j.y||[];R=a.map((p,E)=>({x:p,y:c[E]}))}if(T){const a=T.x||[],c=T.y||[];y=a.map((p,E)=>({x:p,y:c[E]}))}const x=(n||[]).find(a=>a&&a.type==="candlestick");let A=null,D=null;if(x&&x.x&&x.x.length>0){const a=x.x.map(c=>new Date(c));A=Math.min(...a.map(c=>c.getTime())),D=Math.max(...a.map(c=>c.getTime()))}else{const a=[...(R||[]).map(c=>c.x),...(y||[]).map(c=>c.x)].filter(Boolean);if(a.length>0){const c=a.map(p=>new Date(p));A=Math.min(...c.map(p=>p.getTime())),D=Math.max(...c.map(p=>p.getTime()))}else A=Date.now()-1e3*60*60*24*30,D=Date.now()}let F,$;if(x&&x.low&&x.high&&x.low.length>0&&x.high.length>0){const a=x.low.map(E=>Number(E)).filter(E=>Number.isFinite(E)),c=x.high.map(E=>Number(E)).filter(E=>Number.isFinite(E)),p=[...a,...c];F=Math.min(...p.length?p:[0]),$=Math.max(...p.length?p:[1])}else{const a=[...(R||[]).map(c=>c.y),...(y||[]).map(c=>c.y)].filter(c=>Number.isFinite(c));F=Math.min(...a.length?a:[0]),$=Math.max(...a.length?a:[1])}F===$&&(F=F-1,$=$+1);const q=a=>{const c=new Date(a).getTime();return 60+(C-120)*(c-A)/(D-A)},J=a=>40+(b-80)*($-a)/($-F);for(const a of R){const c=q(a.x),p=J(a.y);i.fillStyle=g.entryMarkerColor,i.beginPath(),i.moveTo(c,p-8),i.lineTo(c-6,p+6),i.lineTo(c+6,p+6),i.closePath(),i.fill()}for(const a of y){const c=q(a.x),p=J(a.y);i.fillStyle=g.exitMarkerColor,i.beginPath(),i.moveTo(c,p+8),i.lineTo(c-6,p-6),i.lineTo(c+6,p-6),i.closePath(),i.fill()}const ce=k.toDataURL("image/png");N||u(ce)}catch(k){console.warn("Failed to generate static image from Plotly or canvas",k)}}return P(),()=>{N=!0}},[m,n,s,e]),s=I.useMemo(()=>m?{...f,images:[{source:m,xref:"paper",yref:"paper",x:0,y:1,sizex:1,sizey:1,sizing:"stretch",layer:"below",opacity:.95}],autosize:!0}:f,[m,f]),d.jsx("div",{"data-testid":"candlestick-chart",style:{width:"100%"},children:t.dates.length===0&&!m&&(!r||(((M=r.entries)==null?void 0:M.length)||0)===0&&(((v=r.exits)==null?void 0:v.length)||0)===0)?d.jsx("p",{"data-testid":"no-data-message",children:"No chart data available"}):d.jsx("div",{"data-testid":"plotly-chart",children:d.jsx("div",{"data-testid":"chart-rendered","data-traces":JSON.stringify(n.length),"data-ticker":e,style:{minHeight:200,display:"flex",alignItems:"center",justifyContent:"center",position:"relative",backgroundColor:"#0f172a",width:"100%"},children:d.jsx("div",{style:{minHeight:200,display:"flex",alignItems:"center",justifyContent:"center",backgroundImage:m?`url(${m})`:void 0,backgroundSize:"cover",backgroundPosition:"center",backgroundRepeat:"no-repeat",width:"100%",height:260},children:d.jsxs("div",{style:{background:"rgba(0,0,0,0.45)",padding:8,borderRadius:6,color:"#fff"},children:[e," • ",n.length," traces"]})})})})})}const Z=6,Fe=28;function Le(){return d.jsxs("svg",{viewBox:"0 0 20 20","aria-hidden":"true",focusable:"false",children:[d.jsx("path",{d:"M4 8V4h4M12 4h4v4M16 12v4h-4M8 16H4v-4",fill:"none",stroke:"currentColor",strokeWidth:"1.8",strokeLinecap:"round",strokeLinejoin:"round"}),d.jsx("path",{d:"M8 4 4 8M12 4l4 4M4 12l4 4M16 12l-4 4",fill:"none",stroke:"currentColor",strokeWidth:"1.8",strokeLinecap:"round",strokeLinejoin:"round"})]})}function Q(e){if(typeof e=="number"&&Number.isFinite(e))return e;if(typeof e=="string"&&e.trim()!==""){const t=Number(e);return Number.isFinite(t)?t:null}return null}function Oe(e){const t=e,r=typeof t.entry_date=="string"?t.entry_date:typeof t.date=="string"?t.date:null,l=Q(t.entry_price??t.price),o=Q(t.shares)??1;return!r||l===null||o<=0?null:{timestamp:r,price:l,amount:l*o}}function se(e,t=1){if(!Number.isFinite(e)||e<=0)return Z;const r=Math.sqrt(e)*t;return Math.max(Z,Math.min(Fe,Number(r.toFixed(2))))}const Ae=se;function ie(e,t,r=5){if(!t||t.length===0)return[];const l=[...t].sort((u,h)=>h.total_pnl-u.total_pnl),o=l.slice(0,r),n=l.slice(Math.max(l.length-r,0)).sort((u,h)=>u.total_pnl-h.total_pnl),f=[],m=new Set;for(const u of o)m.has(u.ticker)||(m.add(u.ticker),f.push({stat:u,group:"top"}));for(const u of n)m.has(u.ticker)||(m.add(u.ticker),f.push({stat:u,group:"bottom"}));return f.map(({stat:u,group:h})=>{const s=e.filter(w=>w.ticker===u.ticker).map(Oe).filter(w=>w!==null).sort((w,M)=>w.timestamp.localeCompare(M.timestamp));return{ticker:u.ticker,totalPnl:u.total_pnl,group:h,purchases:s}})}const ee=({trades:e,tickerStats:t,loading:r=!1,limit:l=5})=>{const{t:o}=Se(),[n,f]=I.useState(null);if(I.useEffect(()=>{if(!n)return;const s=w=>{w.key==="Escape"&&f(null)};return window.addEventListener("keydown",s),()=>window.removeEventListener("keydown",s)},[n]),r)return d.jsx("div",{className:"purchase-charts loading",children:o("chartGallery.loadingCharts")});const u=I.useMemo(()=>ie(e,t,l),[e,t,l]).filter(s=>s.purchases.length>0),h=I.useMemo(()=>{const s=new Map;let w=0,M=0;for(const v of u)v.group==="top"?(w+=1,s.set(`${v.group}-${v.ticker}`,w)):(M+=1,s.set(`${v.group}-${v.ticker}`,M));return s},[u]);return u.length===0?d.jsx("div",{className:"purchase-charts empty",children:o("chartGallery.noPurchaseData")}):d.jsxs("div",{className:"purchase-charts","data-testid":"purchase-charts",children:[d.jsx("div",{className:"purchase-grid",children:u.map(s=>d.jsxs("div",{className:"purchase-card","data-testid":"purchase-chart-card",children:[d.jsxs("div",{className:"purchase-card-title",children:[d.jsx("span",{children:s.ticker}),d.jsxs("div",{className:"purchase-card-actions",children:[d.jsx("span",{className:`badge ${s.group}`,children:s.group==="top"?o("chartGallery.topShort"):o("chartGallery.bottomShort")}),d.jsx("span",{className:`rank-badge ${s.group}`,children:s.group==="top"?o("chartGallery.topRankBadge",{rank:h.get(`${s.group}-${s.ticker}`)??1}):o("chartGallery.bottomRankBadge",{rank:h.get(`${s.group}-${s.ticker}`)??1})}),d.jsx("button",{type:"button",className:"purchase-expand-button","aria-label":o("chartGallery.expandChartFor",{ticker:s.ticker}),title:o("chartGallery.expandChart"),onClick:()=>f(s),children:d.jsx(Le,{})})]})]}),d.jsx("button",{type:"button",className:"purchase-chart-button","aria-label":o("chartGallery.expandChart"),onClick:()=>f(s),children:d.jsx(Y,{ticker:s.ticker,data:{dates:[],open:[],high:[],low:[],close:[],volume:[]},markers:{entries:s.purchases.map(w=>({date:w.timestamp,price:w.price})),exits:[]},width:420,height:240})})]},`${s.group}-${s.ticker}`))}),n?d.jsx("div",{className:"purchase-lightbox",role:"dialog","aria-modal":"true","aria-label":o("chartGallery.expandChart"),onClick:()=>f(null),children:d.jsxs("div",{className:"purchase-lightbox-content",onClick:s=>s.stopPropagation(),children:[d.jsxs("div",{className:"purchase-lightbox-header",children:[d.jsxs("div",{children:[d.jsx("strong",{children:n.ticker}),d.jsx("p",{children:n.group==="top"?o("chartGallery.topPerformerDetail"):o("chartGallery.bottomPerformerDetail")})]}),d.jsx("button",{type:"button",className:"purchase-expand-button",onClick:()=>f(null),children:o("nav.close")})]}),d.jsx(Y,{ticker:n.ticker,data:{dates:[],open:[],high:[],low:[],close:[],volume:[]},markers:{entries:n.purchases.map(s=>({date:s.timestamp,price:s.price})),exits:[]},width:960,height:560})]})}):null,d.jsx("style",{children:`
        .purchase-charts {
          padding: 20px;
        }
        .purchase-charts.loading,
        .purchase-charts.empty {
          min-height: 260px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #64748b;
        }
        .purchase-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
          gap: 14px;
        }
        .purchase-card {
          border: 1px solid #e2e8f0;
          border-radius: 8px;
          background: #fff;
          overflow: hidden;
        }
        .purchase-card-title {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px 10px;
          border-bottom: 1px solid #e2e8f0;
          font-size: 12px;
          font-weight: 600;
          color: #0f172a;
        }
        .purchase-card-actions {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .purchase-chart-button {
          width: 100%;
          padding: 0;
          border: none;
          background: transparent;
          cursor: zoom-in;
        }
        .purchase-expand-button {
          width: 34px;
          height: 34px;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          border: 1px solid #cbd5e1;
          border-radius: 999px;
          background: #f8fafc;
          color: #0f172a;
          cursor: pointer;
          box-shadow: 0 4px 10px rgba(15, 23, 42, 0.08);
        }
        .purchase-expand-button svg {
          width: 18px;
          height: 18px;
        }
        .purchase-expand-button:hover {
          background: #e2e8f0;
        }
        .badge {
          font-size: 10px;
          padding: 2px 6px;
          border-radius: 10px;
          letter-spacing: 0.4px;
        }
        .rank-badge {
          min-width: 48px;
          padding: 4px 8px;
          border-radius: 999px;
          font-size: 11px;
          font-weight: 700;
          text-align: center;
          line-height: 1;
        }
        .badge.top {
          background: #dcfce7;
          color: #166534;
        }
        .rank-badge.top {
          background: #dbeafe;
          color: #1d4ed8;
        }
        .badge.bottom {
          background: #fee2e2;
          color: #991b1b;
        }
        .rank-badge.bottom {
          background: #fee2e2;
          color: #b91c1c;
        }
        .purchase-lightbox {
          position: fixed;
          inset: 0;
          background: rgba(15, 23, 42, 0.88);
          z-index: 1000;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 16px;
        }
        .purchase-lightbox-content {
          width: min(100%, 1040px);
          max-height: 100%;
          overflow: auto;
          background: #0f172a;
          border-radius: 18px;
          padding: 16px;
        }
        .purchase-lightbox-header {
          display: flex;
          justify-content: space-between;
          gap: 12px;
          align-items: center;
          color: #e2e8f0;
          margin-bottom: 12px;
        }
        .purchase-lightbox-header p {
          margin: 4px 0 0;
          color: #94a3b8;
          font-size: 13px;
        }
        @media (max-width: 768px) {
          .purchase-grid {
            grid-template-columns: 1fr;
          }
          .purchase-charts {
            padding: 8px 0;
          }
        }
      `})]})},Ge=Object.freeze(Object.defineProperty({__proto__:null,TopBottomPurchaseCharts:ee,buildTopBottomPurchaseCharts:ie,calculateMarkerSize:se,calculateSymbolSize:Ae,default:ee},Symbol.toStringTag,{value:"Module"}));export{Ge as T,Re as b,Ue as i,d as j,Se as u};
