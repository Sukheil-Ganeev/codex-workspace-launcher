function submitForm(e){
    e.preventDefault();
    const form=e.target;
    const status=document.getElementById('status');
    status.textContent='Sending...';
    status.className='success';
    status.style.display='block';
    setTimeout(function(){
        status.textContent='Thank you! We will contact you soon.';
        status.className='success';
        form.reset();
    },1000);
}
