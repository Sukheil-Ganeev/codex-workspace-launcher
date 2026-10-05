const prices={morning:{adult:350,child:250},evening:{adult:420,child:300},night:{adult:650,child:450}};
function updateTourDetails(){calculatePrice();}
function calculatePrice(){
    const form=document.getElementById('bookingForm');
    const tour=form.tour.value;
    const adults=parseInt(form.adults.value)||0;
    const children=parseInt(form.children.value)||0;
    if(!tour){document.getElementById('summary').innerHTML='<p>Select a tour</p>';return;}
    const p=prices[tour];
    const total=adults*p.adult+children*p.child;
    document.getElementById('summary').innerHTML=`<div class="summary-item"><span>Total:</span><span>${total} AED</span></div>`;
}
function submitBooking(e){e.preventDefault();alert('Booking confirmed!');e.target.reset();}
