const tours=[
    {name:'Morning Safari',desc:'Sunrise adventure',duration:'5h',adultAED:350,childAED:250},
    {name:'Evening Safari',desc:'Sunset & dinner',duration:'6h',adultAED:420,childAED:300},
    {name:'Night Safari VIP',desc:'Full experience',duration:'7h',adultAED:650,childAED:450}
];
const rates={AED:1,USD:0.27,RUB:27};

function populateTable(){
    const tbody=document.getElementById('priceTableBody');
    tbody.innerHTML='';
    const currency=document.getElementById('currencySelect').value;
    const groupSize=parseInt(document.getElementById('groupSize').value);
    const rate=rates[currency];
    tours.forEach(tour=>{
        const adultPrice=Math.round(tour.adultAED*rate);
        const childPrice=Math.round(tour.childAED*rate);
        const totalPrice=adultPrice*groupSize;
        tbody.innerHTML+=`<tr><td><strong>${tour.name}</strong></td><td>${tour.desc}</td><td>${tour.duration}</td><td>${adultPrice} ${currency}</td><td>${childPrice} ${currency}</td><td><strong>${totalPrice} ${currency}</strong></td></tr>`;
    });
}

function changeCurrency(){populateTable();}
function updatePrices(){populateTable();}
document.addEventListener('DOMContentLoaded',populateTable);
