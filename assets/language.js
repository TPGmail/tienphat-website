(()=>{'use strict';
const key='tp-lang-v2',valid=l=>['vi','en','zh'].includes(l);const fixed=document.documentElement.getAttribute('data-site-locale');let current=valid(fixed)?fixed:'en';
try{if(!valid(fixed)){const saved=localStorage.getItem(key);if(valid(saved))current=saved}}catch{}
const api={get:()=>current,set(lang){if(valid(fixed))lang=fixed;else if(!valid(lang))lang='en';const changed=current!==lang;current=lang;try{localStorage.setItem(key,lang)}catch{}if(changed)window.dispatchEvent(new CustomEvent('tp:language',{detail:lang}));return lang}};
window.TPLanguage=api;
window.addEventListener('storage',e=>{if(e.key===key&&!valid(fixed))api.set(e.newValue)});
window.addEventListener('pageshow',()=>{try{api.set(localStorage.getItem(key)||current)}catch{}});
})();