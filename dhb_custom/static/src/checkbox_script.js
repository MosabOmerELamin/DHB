// // custom_script.js
// document.addEventListener("DOMContentLoaded", function () {
//     var parentElement = document.getElementById("signup_fields");

//     if (!parentElement) {
//         console.error("Parent element not found");
//         return;
//     }

//     // Add event listener to parent element
//     parentElement.addEventListener("change", function (event) {
//         var target = event.target;

//         // Check if the target element matches the dynamically generated element
//         if (target.matches("#is_studied")) {
//             // Handle the change event for the dynamically generated element
//             var additionalFieldWrapper = document.getElementById("reason");
//             toggleAdditionalField(target, additionalFieldWrapper);
//         }
//     });

//     // Function to toggle the additional field based on checkbox state
//     function toggleAdditionalField(checkbox, additionalFieldWrapper) {
//         additionalFieldWrapper.style.display = checkbox.checked ? "block" : "none";
//     }

//     // Call the toggle function initially to set the initial state
//     var initialCheckbox = document.getElementById("is_studied");
//     var additionalFieldWrapper = document.getElementById("reason");
//     toggleAdditionalField(initialCheckbox, additionalFieldWrapper);
// });
document.addEventListener("DOMContentLoaded", function () {
    var isStudiedCheckbox = document.getElementById("is_studied");
    var reasonField = document.getElementById("reason");

    // Function to toggle visibility of the reason field
    function toggleReasonField() {
        reasonField.style.display = isStudiedCheckbox.checked ? "block" : "none";
    }

    // Initial call to set the initial state
    toggleReasonField();

    // Event listener to update visibility when the checkbox value changes
    isStudiedCheckbox.addEventListener("change", toggleReasonField);
});
