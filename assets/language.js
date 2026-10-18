(()=>{'use strict';
const key='tp-lang-v2',valid=l=>['vi','en','zh'].includes(l);let current='en';
try{const saved=localStorage.getItem(key);if(valid(saved))current=saved}catch{}
const api={get:()=>current,set(lang){if(!valid(lang))lang='en';const changed=current!==lang;current=lang;try{localStorage.setItem(key,lang)}catch{}if(changed)window.dispatchEvent(new CustomEvent('tp:language',{detail:lang}));return lang}};
window.TPLanguage=api;
window.addEventListener('storage',e=>{if(e.key===key)api.set(e.newValue)});
window.addEventListener('pageshow',()=>{try{api.set(localStorage.getItem(key)||current)}catch{}});
})();