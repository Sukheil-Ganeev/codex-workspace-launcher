const childDiscount=0.7;
function updateDetails(){}
function calculate(){
    const tour=parseFloat(document.getElementById('tourSelect').value);
    const adults=parseInt(document.getElementById('adults').value)||1;
    const children=parseInt(document.getElementById('children').value)||0;
    if(!tour){alert('Please select a tour');return;}
    const adultTotal=tour*adults;
    const childTotal=tour*childDiscount*children;
    const total=adultTotal+childTotal;
    const html=`<div class="result-item"><span>Adults (${adults}):</span><span>${adultTotal} AED</span></div>
    <div class="result-item"><span>Children (${children}):</span><span>${childTotal.toFixed(0)} AED</span></div>
    <div class="result-total">Total: ${total.toFixed(0)} AED</div>`;
    const res=document.getElementById('result');
    res.innerHTML=html;
    res.classList.add('show');
}
