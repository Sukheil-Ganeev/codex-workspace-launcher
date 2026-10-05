let bookings=JSON.parse(localStorage.getItem('bookings'))||[];
function loadBookings(){
    if(bookings.length===0){
        document.getElementById('noData').textContent='No bookings yet';
        return;
    }
    const tbody=document.getElementById('tableBody');
    tbody.innerHTML='';
    bookings.forEach((b,i)=>{
        const row=`<tr><td>${b.name}</td><td>${b.email}</td><td>${b.tour}</td><td>${b.date}</td><td>Confirmed</td></tr>`;
        tbody.innerHTML+=row;
    });
    document.getElementById('bookingTable').style.display='table';
    document.getElementById('noData').style.display='none';
}
function addBooking(e){
    e.preventDefault();
    const form=e.target;
    const booking={
        name:form[0].value,
        email:form[1].value,
        date:form[2].value,
        tour:form[3].value
    };
    bookings.push(booking);
    localStorage.setItem('bookings',JSON.stringify(bookings));
    alert('Booking added!');
    form.reset();
    loadBookings();
}
