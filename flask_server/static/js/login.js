// Fuad Suleymanli

const sign_in_btn = document.querySelector("#sign-in-btn");
const sign_up_btn = document.querySelector("#sign-up-btn");
const container = document.querySelector(".container");

sign_up_btn.addEventListener("click", () => {
  container.classList.add("sign-up-mode");
});

sign_in_btn.addEventListener("click", () => {
  container.classList.remove("sign-up-mode");
});
// Get the URL parameters
const urlParams = new URLSearchParams(window.location.search);

// Check if the 'mode' parameter is set to 'signup'
if (urlParams.get('mode') === 'signup') {
  document.querySelector('.container').classList.add('sign-up-mode');
}

