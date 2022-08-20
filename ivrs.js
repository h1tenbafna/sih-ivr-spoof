// const inputopt = prompt('enter your input: ');
// const input = document.querySelector('#inputopt');

// input.innerHTML= inputopt;

const input = document.querySelector('#nameCall');
const store = document.querySelector('#dname');
input.value = 'Name which will come from ivrs'
dname.innerHTML = input;


const res = document.querySelector('#resultCall');


const resultBtn = document.querySelector('#resultBtn');
const result = document.querySelector('.result');

resultBtn.addEventListener('click',()=>{
    res.innerHTML = 'Likely Spam';
    // result.classList.toggle('active');

})

const fwdBtn = document.querySelector('#fwdBtn');

fwdBtn.addEventListener('click',()=>{
    res.innerHTML = 'Forwarding Call';
    // result.classList.toggle('active');

})
