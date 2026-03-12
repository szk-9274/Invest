import{r as _,R as j}from"./plotly-core-CJ9sSumU.js";var ue={exports:{}},Y={};/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var be=_,we=Symbol.for("react.element"),Ce=Symbol.for("react.fragment"),ve=Object.prototype.hasOwnProperty,ke=be.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner,Ne={key:!0,ref:!0,__self:!0,__source:!0};function pe(e,t,r){var l,n={},o=null,u=null;r!==void 0&&(o=""+r),t.key!==void 0&&(o=""+t.key),t.ref!==void 0&&(u=t.ref);for(l in t)ve.call(t,l)&&!Ne.hasOwnProperty(l)&&(n[l]=t[l]);if(e&&e.defaultProps)for(l in t=e.defaultProps,t)n[l]===void 0&&(n[l]=t[l]);return{$$typeof:we,type:e,key:o,ref:u,props:n,_owner:ke.current}}Y.Fragment=Ce;Y.jsx=pe;Y.jsxs=pe;ue.exports=Y;var d=ue.exports;const je=(e,t,r,l)=>{var o,u,y,p;const n=[r,{code:t,...l||{}}];if((u=(o=e==null?void 0:e.services)==null?void 0:o.logger)!=null&&u.forward)return e.services.logger.forward(n,"warn","react-i18next::",!0);$(n[0])&&(n[0]=`react-i18next:: ${n[0]}`),(p=(y=e==null?void 0:e.services)==null?void 0:y.logger)!=null&&p.warn?e.services.logger.warn(...n):console!=null&&console.warn&&console.warn(...n)},oe={},X=(e,t,r,l)=>{$(r)&&oe[r]||($(r)&&(oe[r]=new Date),je(e,t,r,l))},he=(e,t)=>()=>{if(e.isInitialized)t();else{const r=()=>{setTimeout(()=>{e.off("initialized",r)},0),t()};e.on("initialized",r)}},Z=(e,t,r)=>{e.loadNamespaces(t,he(e,r))},ne=(e,t,r,l)=>{if($(r)&&(r=[r]),e.options.preload&&e.options.preload.indexOf(t)>-1)return Z(e,r,l);r.forEach(n=>{e.options.ns.indexOf(n)<0&&e.options.ns.push(n)}),e.loadLanguages(t,he(e,l))},Ee=(e,t,r={})=>!t.languages||!t.languages.length?(X(t,"NO_LANGUAGES","i18n.languages were undefined or empty",{languages:t.languages}),!0):t.hasLoadedNamespace(e,{lng:r.lng,precheck:(l,n)=>{if(r.bindI18n&&r.bindI18n.indexOf("languageChanging")>-1&&l.services.backendConnector.backend&&l.isLanguageChangingTo&&!n(l.isLanguageChangingTo,e))return!1}}),$=e=>typeof e=="string",Te=e=>typeof e=="object"&&e!==null,Se=/&(?:amp|#38|lt|#60|gt|#62|apos|#39|quot|#34|nbsp|#160|copy|#169|reg|#174|hellip|#8230|#x2F|#47);/g,Pe={"&amp;":"&","&#38;":"&","&lt;":"<","&#60;":"<","&gt;":">","&#62;":">","&apos;":"'","&#39;":"'","&quot;":'"',"&#34;":'"',"&nbsp;":" ","&#160;":" ","&copy;":"©","&#169;":"©","&reg;":"®","&#174;":"®","&hellip;":"…","&#8230;":"…","&#x2F;":"/","&#47;":"/"},_e=e=>Pe[e],Me=e=>e.replace(Se,_e);let Q={bindI18n:"languageChanged",bindI18nStore:"",transEmptyNodeValue:"",transSupportBasicHtmlNodes:!0,transWrapTextNodes:"",transKeepBasicHtmlNodesFor:["br","strong","i","p"],useSuspense:!0,unescape:Me};const Re=(e={})=>{Q={...Q,...e}},Ie=()=>Q;let fe;const Le=e=>{fe=e},$e=()=>fe,Ze={type:"3rdParty",init(e){Re(e.options.react),Le(e)}},Fe=_.createContext();class Ae{constructor(){this.usedNamespaces={}}addUsedNamespaces(t){t.forEach(r=>{this.usedNamespaces[r]||(this.usedNamespaces[r]=!0)})}getUsedNamespaces(){return Object.keys(this.usedNamespaces)}}const Oe=(e,t)=>{const r=_.useRef();return _.useEffect(()=>{r.current=e},[e,t]),r.current},me=(e,t,r,l)=>e.getFixedT(t,r,l),ze=(e,t,r,l)=>_.useCallback(me(e,t,r,l),[e,t,r,l]),De=(e,t={})=>{var z,D,g,C;const{i18n:r}=t,{i18n:l,defaultNS:n}=_.useContext(Fe)||{},o=r||l||$e();if(o&&!o.reportNamespaces&&(o.reportNamespaces=new Ae),!o){X(o,"NO_I18NEXT_INSTANCE","useTranslation: You will need to pass in an i18next instance by using initReactI18next");const f=(m,i)=>$(i)?i:Te(i)&&$(i.defaultValue)?i.defaultValue:Array.isArray(m)?m[m.length-1]:m,w=[f,{},!1];return w.t=f,w.i18n={},w.ready=!1,w}(z=o.options.react)!=null&&z.wait&&X(o,"DEPRECATED_OPTION","useTranslation: It seems you are still using the old wait option, you may migrate to the new useSuspense behaviour.");const u={...Ie(),...o.options.react,...t},{useSuspense:y,keyPrefix:p}=u;let a=n||((D=o.options)==null?void 0:D.defaultNS);a=$(a)?[a]:a||["translation"],(C=(g=o.reportNamespaces).addUsedNamespaces)==null||C.call(g,a);const v=(o.isInitialized||o.initializedStoreOnce)&&a.every(f=>Ee(f,o,u)),b=ze(o,t.lng||null,u.nsMode==="fallback"?a:a[0],p),M=()=>b,N=()=>me(o,t.lng||null,u.nsMode==="fallback"?a:a[0],p),[I,S]=_.useState(M);let R=a.join();t.lng&&(R=`${t.lng}${R}`);const H=Oe(R),P=_.useRef(!0);_.useEffect(()=>{const{bindI18n:f,bindI18nStore:w}=u;P.current=!0,!v&&!y&&(t.lng?ne(o,t.lng,a,()=>{P.current&&S(N)}):Z(o,a,()=>{P.current&&S(N)})),v&&H&&H!==R&&P.current&&S(N);const m=()=>{P.current&&S(N)};return f&&(o==null||o.on(f,m)),w&&(o==null||o.store.on(w,m)),()=>{P.current=!1,o&&f&&(f==null||f.split(" ").forEach(i=>o.off(i,m))),w&&o&&w.split(" ").forEach(i=>o.store.off(i,m))}},[o,R]),_.useEffect(()=>{P.current&&v&&S(M)},[o,p,v]);const F=[I,o,v];if(F.t=I,F.i18n=o,F.ready=v,v||!v&&!y)return F;throw new Promise(f=>{t.lng?ne(o,t.lng,a,()=>f()):Z(o,a,()=>f())})},J={},Ue=((J==null?void 0:J.VITE_API_URL)??"").trim(),V=(Ue||"/api").replace(/\/$/,"");function Ge(){var e;return typeof window<"u"&&((e=window.location)!=null&&e.origin)?window.location.origin:"http://localhost"}function ae(e){const t=e.startsWith("/")?e:`/${e}`;return/^https?:\/\//.test(V)?`${V}${t}`:new URL(`${V}${t}`,Ge()).toString()}const Be="modulepreload",He=function(e){return"/"+e},se={},We=function(t,r,l){let n=Promise.resolve();if(r&&r.length>0){document.getElementsByTagName("link");const u=document.querySelector("meta[property=csp-nonce]"),y=(u==null?void 0:u.nonce)||(u==null?void 0:u.getAttribute("nonce"));n=Promise.allSettled(r.map(p=>{if(p=He(p),p in se)return;se[p]=!0;const a=p.endsWith(".css"),v=a?'[rel="stylesheet"]':"";if(document.querySelector(`link[href="${p}"]${v}`))return;const b=document.createElement("link");if(b.rel=a?"stylesheet":Be,a||(b.as="script"),b.crossOrigin="",b.href=p,y&&b.setAttribute("nonce",y),document.head.appendChild(b),a)return new Promise((M,N)=>{b.addEventListener("load",M),b.addEventListener("error",()=>N(new Error(`Unable to preload CSS for ${p}`)))})}))}function o(u){const y=new Event("vite:preloadError",{cancelable:!0});if(y.payload=u,window.dispatchEvent(y),!y.defaultPrevented)throw u}return n.then(u=>{for(const y of u||[])y.status==="rejected"&&o(y.reason);return t().catch(o)})},h={background:"#131722",gridColor:"#2a2e39",textColor:"#d1d4dc",upColor:"#26a69a",downColor:"#ef5350",sma20Color:"#00bcd4",sma50Color:"#ffeb3b",sma200Color:"#e91e63",volumeUpColor:"rgba(38, 166, 154, 0.5)",volumeDownColor:"rgba(239, 83, 80, 0.5)",entryMarkerColor:"#26a69a",exitMarkerColor:"#ef5350"};function Ye(e,t){const r=[];r.push({type:"candlestick",x:e.dates,open:e.open,high:e.high,low:e.low,close:e.close,increasing:{line:{color:h.upColor}},decreasing:{line:{color:h.downColor}},name:"Price",xaxis:"x",yaxis:"y"});const l=e.close.map((n,o)=>o===0||n>=e.close[o-1]?h.volumeUpColor:h.volumeDownColor);return r.push({type:"bar",x:e.dates,y:e.volume,marker:{color:l},name:"Volume",xaxis:"x",yaxis:"y2"}),e.sma20&&r.push({type:"scatter",mode:"lines",x:e.dates,y:e.sma20,line:{color:h.sma20Color,width:1},name:"SMA 20",xaxis:"x",yaxis:"y"}),e.sma50&&r.push({type:"scatter",mode:"lines",x:e.dates,y:e.sma50,line:{color:h.sma50Color,width:1},name:"SMA 50",xaxis:"x",yaxis:"y"}),e.sma200&&r.push({type:"scatter",mode:"lines",x:e.dates,y:e.sma200,line:{color:h.sma200Color,width:1},name:"SMA 200",xaxis:"x",yaxis:"y"}),t&&(t.entries.length>0&&r.push({type:"scatter",mode:"markers",x:t.entries.map(n=>n.date),y:t.entries.map(n=>n.price),marker:{symbol:"triangle-up",size:14,color:h.entryMarkerColor},name:"Entry",xaxis:"x",yaxis:"y",text:t.entries.map(n=>`Entry: $${n.price.toFixed(2)}`),hoverinfo:"text+x"}),t.exits.length>0&&r.push({type:"scatter",mode:"markers",x:t.exits.map(n=>n.date),y:t.exits.map(n=>n.price),marker:{symbol:"triangle-down",size:14,color:h.exitMarkerColor},name:"Exit",xaxis:"x",yaxis:"y",text:t.exits.map(n=>`Exit: $${n.price.toFixed(2)}${n.pnl!==void 0?` (P&L: $${n.pnl.toFixed(2)})`:""}`),hoverinfo:"text+x"})),r}function qe(e,t,r){return{title:{text:e,font:{color:h.textColor,size:16}},paper_bgcolor:h.background,plot_bgcolor:h.background,font:{color:h.textColor},xaxis:{gridcolor:h.gridColor,rangeslider:{visible:!1},type:"date"},yaxis:{gridcolor:h.gridColor,side:"right",domain:[.3,1],title:"Price"},yaxis2:{gridcolor:h.gridColor,domain:[0,.25],title:"Volume"},width:t||1200,height:r||700,showlegend:!0,legend:{bgcolor:"rgba(19, 23, 34, 0.8)",font:{color:h.textColor}},dragmode:"pan"}}function ie({ticker:e,data:t,markers:r,width:l,height:n}){var z,D;const o=Ye(t,r),u=qe(e,l,n),[y,p]=j.useState("ALL"),[a,v]=j.useState(null),[b,M]=j.useState(null),[N,I]=j.useState(null),S=j.useRef(null),R=j.useCallback(async g=>{if(!(typeof window>"u"))try{const C=await fetch(ae(`/backtest/latest?range=${encodeURIComponent(g)}`));if(!C.ok)return;const f=await C.json(),w=f&&f.charts||{},m=Object.keys(w||{});let i=m.find(k=>k===`${e}_price_chart`)||m.find(k=>k===e)||m.find(k=>k.includes(e))||m.find(k=>k.includes("_price_chart"));!i&&m.length>0&&(i=m[0]),i&&w[i]&&M(w[i])}catch(C){console.warn("Failed to fetch chart for period",C)}},[e]),H=j.useCallback(async g=>{if(!(typeof window>"u"))try{const C=await fetch(ae(`/backtest/ohlc?ticker=${encodeURIComponent(e)}&range=${encodeURIComponent(g)}`));if(!C.ok){console.warn("OHLC fetch returned",C.status),I(null);return}const f=await C.json();if(f&&Array.isArray(f.data)&&f.data.length>0){const w=f.data.map(m=>({time:m.time,open:m.open,high:m.high,low:m.low,close:m.close,volume:m.volume}));I(w)}else I(null)}catch(C){console.warn("Failed to fetch OHLC",C),I(null)}},[e]);j.useEffect(()=>{async function g(){try{await R(y)}catch(C){console.warn("fetchChartForPeriod failed",C)}}return g(),()=>{}},[e,y,R]),j.useEffect(()=>{let g=null,C=null,f=null,w=!0;return(async()=>{if(S.current&&!(!N||N.length===0))try{const i=await We(()=>import("./lightweight-chart-core-CuHrsbLW.js"),[]);if(!w)return;S.current.innerHTML="",g=i.createChart(S.current,{layout:{background:{color:h.background},textColor:h.textColor},width:l||800,height:n||450,rightPriceScale:{visible:!0}}),C=g.addCandlestickSeries({upColor:h.upColor,downColor:h.downColor,wickUpColor:h.upColor,wickDownColor:h.downColor}),C.setData(N),f=g.addHistogramSeries({priceFormat:{type:"volume"},scaleMargins:{top:.8,bottom:0}}),f.setData(N.map(k=>({time:k.time,value:k.volume,color:k.close>=k.open?h.volumeUpColor:h.volumeDownColor})))}catch(i){console.warn("lightweight-charts failed to load or render",i)}})(),()=>{w=!1,g&&g.remove&&g.remove()}},[N,l,n]);let P=u;return j.useEffect(()=>{let g=!1;async function C(){try{if(b||typeof document>"u"||typeof navigator<"u"&&navigator.userAgent.includes("jsdom"))return;const f=document.createElement("canvas"),w=1200,m=700;f.width=w,f.height=m;const i=f.getContext("2d");if(!i)return;i.fillStyle=h.background,i.fillRect(0,0,w,m),i.strokeStyle=h.gridColor,i.lineWidth=1;const k=6,ee=6;for(let s=1;s<k;s++){const c=Math.round(w*s/k);i.beginPath(),i.moveTo(c,0),i.lineTo(c,m),i.stroke()}for(let s=1;s<ee;s++){const c=Math.round(m*s/ee);i.beginPath(),i.moveTo(0,c),i.lineTo(w,c),i.stroke()}i.fillStyle=h.textColor,i.font="16px sans-serif",i.fillText(e,12,24);const A=(o||[]).find(s=>s&&(s.name==="Entry"||s.name==="Exit"));let U=[],G=[];if(A){const s=A.x||[],c=A.y||[];for(let x=0;x<s.length;x++)A.marker&&A.marker.symbol==="triangle-up"||A.name==="Entry"?U.push({x:s[x],y:c[x]}):G.push({x:s[x],y:c[x]})}const q=(o||[]).find(s=>s&&s.name==="Entry"),K=(o||[]).find(s=>s&&s.name==="Exit");if(q){const s=q.x||[],c=q.y||[];U=s.map((x,T)=>({x,y:c[T]}))}if(K){const s=K.x||[],c=K.y||[];G=s.map((x,T)=>({x,y:c[T]}))}const E=(o||[]).find(s=>s&&s.type==="candlestick");let B=null,W=null;if(E&&E.x&&E.x.length>0){const s=E.x.map(c=>new Date(c));B=Math.min(...s.map(c=>c.getTime())),W=Math.max(...s.map(c=>c.getTime()))}else{const s=[...(U||[]).map(c=>c.x),...(G||[]).map(c=>c.x)].filter(Boolean);if(s.length>0){const c=s.map(x=>new Date(x));B=Math.min(...c.map(x=>x.getTime())),W=Math.max(...c.map(x=>x.getTime()))}else B=Date.now()-1e3*60*60*24*30,W=Date.now()}let O,L;if(E&&E.low&&E.high&&E.low.length>0&&E.high.length>0){const s=E.low.map(T=>Number(T)).filter(T=>Number.isFinite(T)),c=E.high.map(T=>Number(T)).filter(T=>Number.isFinite(T)),x=[...s,...c];O=Math.min(...x.length?x:[0]),L=Math.max(...x.length?x:[1])}else{const s=[...(U||[]).map(c=>c.y),...(G||[]).map(c=>c.y)].filter(c=>Number.isFinite(c));O=Math.min(...s.length?s:[0]),L=Math.max(...s.length?s:[1])}O===L&&(O=O-1,L=L+1);const te=s=>{const c=new Date(s).getTime();return 60+(w-120)*(c-B)/(W-B)},re=s=>40+(m-80)*(L-s)/(L-O);for(const s of U){const c=te(s.x),x=re(s.y);i.fillStyle=h.entryMarkerColor,i.beginPath(),i.moveTo(c,x-8),i.lineTo(c-6,x+6),i.lineTo(c+6,x+6),i.closePath(),i.fill()}for(const s of G){const c=te(s.x),x=re(s.y);i.fillStyle=h.exitMarkerColor,i.beginPath(),i.moveTo(c,x+8),i.lineTo(c-6,x-6),i.lineTo(c+6,x-6),i.closePath(),i.fill()}const ye=f.toDataURL("image/png");g||M(ye)}catch(f){console.warn("Failed to generate static image from Plotly or canvas",f)}}return C(),()=>{g=!0}},[b,o,P,e]),P=j.useMemo(()=>b?{...u,images:[{source:b,xref:"paper",yref:"paper",x:0,y:1,sizex:1,sizey:1,sizing:"stretch",layer:"below",opacity:.95}],autosize:!0}:u,[b,u]),d.jsxs("div",{"data-testid":"candlestick-chart",style:{width:"100%"},children:[d.jsxs("div",{style:{display:"flex",alignItems:"center",gap:8,marginBottom:8},children:[d.jsx("label",{style:{color:h.textColor},children:"Period:"}),d.jsxs("select",{"aria-label":"Chart period",value:y,onChange:g=>{const C=g.target.value;p(C)},style:{padding:"6px 8px",borderRadius:6},children:[d.jsx("option",{value:"1M",children:"1M"}),d.jsx("option",{value:"3M",children:"3M"}),d.jsx("option",{value:"6M",children:"6M"}),d.jsx("option",{value:"1Y",children:"1Y"}),d.jsx("option",{value:"ALL",children:"All"})]}),d.jsx("label",{style:{color:h.textColor,marginLeft:6},children:"Year:"}),d.jsx("div",{role:"group","aria-label":"Year selector",style:{display:"flex",gap:6},children:["2020","2021","2022","2023","2024","2025"].map(g=>d.jsx("button",{onClick:()=>{v(g),p("ALL"),R(g),H(g)},style:{padding:"6px 8px",borderRadius:6,background:a===g?"#243447":"transparent",color:h.textColor,border:"1px solid rgba(255,255,255,0.06)"},"aria-pressed":a===g,children:g},g))}),d.jsx("div",{style:{marginLeft:"auto",color:"rgba(209,212,220,0.9)"},children:y==="ALL"?a||"Full range":y})]}),t.dates.length===0&&!b&&(!r||(((z=r.entries)==null?void 0:z.length)||0)===0&&(((D=r.exits)==null?void 0:D.length)||0)===0)&&!N?d.jsx("p",{"data-testid":"no-data-message",children:"No chart data available"}):d.jsx("div",{"data-testid":"plotly-chart",children:d.jsx("div",{ref:S,"data-testid":"chart-rendered","data-traces":JSON.stringify(o.length),"data-ticker":e,style:{minHeight:200,display:"flex",alignItems:"center",justifyContent:"center",position:"relative",backgroundColor:"#0f172a",width:"100%"},children:!N&&d.jsx("div",{style:{minHeight:200,display:"flex",alignItems:"center",justifyContent:"center",backgroundImage:b?`url(${b})`:void 0,backgroundSize:"cover",backgroundPosition:"center",backgroundRepeat:"no-repeat",width:"100%",height:260},children:d.jsxs("div",{style:{background:"rgba(0,0,0,0.45)",padding:8,borderRadius:6,color:"#fff"},children:[e," • ",o.length," traces"]})})})})]})}const le=6,Ke=28;function ce(e){if(typeof e=="number"&&Number.isFinite(e))return e;if(typeof e=="string"&&e.trim()!==""){const t=Number(e);return Number.isFinite(t)?t:null}return null}function Je(e){const t=e,r=typeof t.entry_date=="string"?t.entry_date:typeof t.date=="string"?t.date:null,l=ce(t.entry_price??t.price),n=ce(t.shares)??1;return!r||l===null||n<=0?null:{timestamp:r,price:l,amount:l*n}}function ge(e,t=1){if(!Number.isFinite(e)||e<=0)return le;const r=Math.sqrt(e)*t;return Math.max(le,Math.min(Ke,Number(r.toFixed(2))))}const Ve=ge;function xe(e,t,r=5){if(!t||t.length===0)return[];const l=[...t].sort((p,a)=>a.total_pnl-p.total_pnl),n=l.slice(0,r),o=l.slice(Math.max(l.length-r,0)).sort((p,a)=>p.total_pnl-a.total_pnl),u=[],y=new Set;for(const p of n)y.has(p.ticker)||(y.add(p.ticker),u.push({stat:p,group:"top"}));for(const p of o)y.has(p.ticker)||(y.add(p.ticker),u.push({stat:p,group:"bottom"}));return u.map(({stat:p,group:a})=>{const v=e.filter(b=>b.ticker===p.ticker).map(Je).filter(b=>b!==null).sort((b,M)=>b.timestamp.localeCompare(M.timestamp));return{ticker:p.ticker,totalPnl:p.total_pnl,group:a,purchases:v}})}const de=({trades:e,tickerStats:t,loading:r=!1,limit:l=5})=>{const{t:n}=De(),[o,u]=j.useState(null);if(j.useEffect(()=>{if(!o)return;const a=v=>{v.key==="Escape"&&u(null)};return window.addEventListener("keydown",a),()=>window.removeEventListener("keydown",a)},[o]),r)return d.jsx("div",{className:"purchase-charts loading",children:n("chartGallery.loadingCharts")});const p=j.useMemo(()=>xe(e,t,l),[e,t,l]).filter(a=>a.purchases.length>0);return p.length===0?d.jsx("div",{className:"purchase-charts empty",children:n("chartGallery.noPurchaseData")}):d.jsxs("div",{className:"purchase-charts","data-testid":"purchase-charts",children:[d.jsx("div",{className:"purchase-grid",children:p.map(a=>d.jsxs("div",{className:"purchase-card","data-testid":"purchase-chart-card",children:[d.jsxs("div",{className:"purchase-card-title",children:[d.jsx("span",{children:a.ticker}),d.jsxs("div",{className:"purchase-card-actions",children:[d.jsx("span",{className:`badge ${a.group}`,children:a.group==="top"?n("chartGallery.topShort"):n("chartGallery.bottomShort")}),d.jsx("button",{type:"button",className:"purchase-expand-button","aria-label":n("chartGallery.expandChart"),onClick:()=>u(a),children:n("chartGallery.expandChart")})]})]}),d.jsx("button",{type:"button",className:"purchase-chart-button","aria-label":n("chartGallery.expandChart"),onClick:()=>u(a),children:d.jsx(ie,{ticker:a.ticker,data:{dates:[],open:[],high:[],low:[],close:[],volume:[]},markers:{entries:a.purchases.map(v=>({date:v.timestamp,price:v.price})),exits:[]},width:420,height:240})})]},`${a.group}-${a.ticker}`))}),o?d.jsx("div",{className:"purchase-lightbox",role:"dialog","aria-modal":"true","aria-label":n("chartGallery.expandChart"),onClick:()=>u(null),children:d.jsxs("div",{className:"purchase-lightbox-content",onClick:a=>a.stopPropagation(),children:[d.jsxs("div",{className:"purchase-lightbox-header",children:[d.jsxs("div",{children:[d.jsx("strong",{children:o.ticker}),d.jsx("p",{children:o.group==="top"?n("chartGallery.topPerformerDetail"):n("chartGallery.bottomPerformerDetail")})]}),d.jsx("button",{type:"button",className:"purchase-expand-button",onClick:()=>u(null),children:n("nav.close")})]}),d.jsx(ie,{ticker:o.ticker,data:{dates:[],open:[],high:[],low:[],close:[],volume:[]},markers:{entries:o.purchases.map(a=>({date:a.timestamp,price:a.price})),exits:[]},width:960,height:560})]})}):null,d.jsx("style",{children:`
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
          border: none;
          border-radius: 999px;
          background: #e2e8f0;
          color: #0f172a;
          font-size: 11px;
          font-weight: 700;
          padding: 6px 10px;
          cursor: pointer;
        }
        .badge {
          font-size: 10px;
          padding: 2px 6px;
          border-radius: 10px;
          letter-spacing: 0.4px;
        }
        .badge.top {
          background: #dcfce7;
          color: #166534;
        }
        .badge.bottom {
          background: #fee2e2;
          color: #991b1b;
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
      `})]})},Qe=Object.freeze(Object.defineProperty({__proto__:null,TopBottomPurchaseCharts:de,buildTopBottomPurchaseCharts:xe,calculateMarkerSize:ge,calculateSymbolSize:Ve,default:de},Symbol.toStringTag,{value:"Module"}));export{Qe as T,We as _,ae as b,Ze as i,d as j,De as u};
