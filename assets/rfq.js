(()=>{'use strict';
  const form=document.getElementById('contact-form');
  if(!form)return;
  const params=new URLSearchParams(window.location.search);
  const material=params.get('material')||'';
  const sample=(params.get('sample')||'').trim().slice(0,100);
  const source=(params.get('source')||'').trim();
  if(['pu','nubuck','leather','other'].includes(material))form.elements.namedItem('material_category').value=material;
  if(sample)form.elements.namedItem('sample_code').value=sample;
  const sourceField=form.elements.namedItem('source_page');
  if(sourceField&&['da-pu-pho-thong.html','da-pu-nubuck.html','da-that.html'].includes(source))sourceField.value=source;
  if(sample){
    const locale=document.documentElement.getAttribute('data-site-locale')||'en';
    const prefix={en:'Selected sample for enquiry: ',vi:'Mã mẫu đang yêu cầu: ',zh:'已选择询价样品：'};
    const note=document.getElementById('rfq-selected');
    if(note){note.textContent=(prefix[locale]||prefix.en)+sample;note.hidden=false;}
  }
})();
