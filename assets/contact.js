(()=>{'use strict';
const labels={vi:{call:'Gọi điện',zalo:'Chat Zalo',group:'Liên hệ Tiến Phát'},en:{call:'Call now',zalo:'Chat on Zalo',group:'Contact Tien Phat'},zh:{call:'拨打电话',zalo:'Zalo 聊天',group:'联系 Tiến Phát'}};
let fabs=document.querySelector('.contact-fabs');
if(!fabs){fabs=document.createElement('div');fabs.className='contact-fabs';fabs.innerHTML='<a class="floating-call" href="tel:+84931792811">☎</a><a class="floating-zalo" href="https://zalo.me/0931792811" target="_blank" rel="noopener noreferrer">Zalo</a>';document.body.appendChild(fabs)}
function render(){const lang=window.TPLanguage?TPLanguage.get():'en',text=labels[lang]||labels.en;fabs.setAttribute('aria-label',text.group);
document.querySelectorAll('.floating-call,.contact-call,.contact-actions a[href^="tel:"]').forEach(a=>{a.setAttribute('aria-label',text.call);a.title=text.call;if(!a.classList.contains('floating-call'))a.textContent=text.call});
document.querySelectorAll('.floating-zalo,.contact-zalo').forEach(a=>{a.setAttribute('aria-label',text.zalo);a.title=text.zalo;if(!a.classList.contains('floating-zalo'))a.textContent=text.zalo});
}
window.addEventListener('tp:language',render);render();
})();