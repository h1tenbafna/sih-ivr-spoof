var response = {
  message: "Somebody Help!",
  number: 9827698237,
  selected_option: 1,
};
function reloadPage() {
  pathname = "/get-call-details";
  $.ajax(
    {
      method: "get",
      url: pathname,
      datatype: "json", 
      contentType: "application/json",
      success: (data) => {
        response = data;
      },
    },
    (data, status) => {}
  );

  console.log(response)

  var message = response.message;
  var option = response.selected_option;
  var phno = response.mob_number;

  const messageInput = document.querySelector("#message");
  const phoneNumber = document.querySelector("#phoneCall");
  const selectedOption = document.querySelector("#inputopt");
  
  messageInput.innerHTML = message;
  selectedOption.innerHTML = option;
  phoneNumber.innerHTML = phno;

  const res = document.querySelector("#resultCall");

  const resultBtn = document.querySelector("#resultBtn");
  const result = document.querySelector(".result");

  // resultBtn.addEventListener("click", () => {
  //   res.innerHTML = "Likely Spam";
  // });

  const fwdBtn = document.querySelector("#fwdBtn");

  // fwdBtn.addEventListener("click", () => {
  //   res.innerHTML = "Forwarding Call";
  // });

  const predicitonmsg = document.querySelector(".prediction");
  const prediction = document.querySelector("#predictionCall");
  const user_input_prediction = response.selected_option;
  if (user_input_prediction == 1) {
    prediction.innerHTML = "Emergency";
  }
  else if(user_input_prediction == 2) {
    prediction.innerHTML = "Help"
  }
  else if(user_input_prediction == 3) {
    prediction.innerHTML = "Enquiry"
  }
  const modelPrediction = document.querySelector("#modelPrediction");
  modelPrediction.innerHTML = response.prediction
  // console.log(response)
  if (prediction.innerText.includes("Emergency")) {
    predicitonmsg.style.backgroundColor = "red";
  } else if (prediction.innerText.includes("Help")) {
    predicitonmsg.style.backgroundColor = "#fab51f";
    predicitonmsg.style.color = "black";
  } else if (prediction.innerText.includes("Enquiry")) {
    predicitonmsg.style.backgroundColor = "green";
    predicitonmsg.style.color = "black";
  } else if (prediction.innerText.includes("Blank")) {
    predicitonmsg.style.backgroundColor = "cyan";
    prediction.style.color = "black";
  } else {
    predicitonmsg.style.backgroundColor = "#14382e";
  }
}

setInterval(reloadPage, 1000);
