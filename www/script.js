document.addEventListener('DOMContentLoaded',function(){
  document.getElementById('year').textContent=new Date().getFullYear();
  const form=document.getElementById('contactForm');
  const notice=document.getElementById('notice');
  form.addEventListener('submit',function(e){
    e.preventDefault();
    const email=form.email.value;
    const msg=form.message.value;
    // This demo does not send messages. Provide a friendly local confirmation.
    notice.textContent = `Thanks — we'll contact ${email} shortly.`;
    form.reset();
  });
});
