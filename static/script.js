"use strict";

// ==========================================
// 1. GET HTML ELEMENTS
// ==========================================

const uploadForm = document.getElementById("uploadForm");
const xrayInput = document.getElementById("xrayInput");
const fileName = document.getElementById("fileName");
const previewArea = document.getElementById("previewArea");
const imagePreview = document.getElementById("imagePreview");
const previewMessage = document.getElementById("previewMessage");
const bodyPartInput = document.getElementById("bodyPart");

const patientIdInput = document.getElementById("patientId");
const patientAgeInput = document.getElementById("patientAge");
const patientGenderInput = document.getElementById("patientGender");

const submitButton = uploadForm
    ? uploadForm.querySelector('button[type="submit"]')
    : null;

let selectedImage = null;

const MAX_FILE_SIZE = 10 * 1024 * 1024;

const ALLOWED_TYPES = [
    "image/png",
    "image/jpeg"
];


// ==========================================
// 2. CHECK REQUIRED ELEMENTS
// ==========================================

if (
    !uploadForm ||
    !xrayInput ||
    !fileName ||
    !previewArea ||
    !imagePreview ||
    !previewMessage ||
    !bodyPartInput ||
    !patientIdInput ||
    !patientAgeInput ||
    !patientGenderInput ||
    !submitButton
) {
    console.error(
        "RadiologyAI: One or more upload form elements are missing."
    );

} else {

    // ==========================================
    // 3. SELECT AND PREVIEW THE IMAGE
    // ==========================================

    xrayInput.addEventListener("change", function () {

        selectedImage = xrayInput.files[0] || null;

        if (!selectedImage) {
            fileName.textContent = "No image selected";
            previewArea.hidden = true;
            imagePreview.removeAttribute("src");
            return;
        }

        if (!ALLOWED_TYPES.includes(selectedImage.type)) {

            alert("Please select a PNG, JPG, or JPEG image.");

            xrayInput.value = "";
            selectedImage = null;

            fileName.textContent = "No image selected";
            previewArea.hidden = true;
            imagePreview.removeAttribute("src");

            return;
        }

        if (selectedImage.size > MAX_FILE_SIZE) {

            alert("The image must be smaller than 10 MB.");

            xrayInput.value = "";
            selectedImage = null;

            fileName.textContent = "No image selected";
            previewArea.hidden = true;
            imagePreview.removeAttribute("src");

            return;
        }

        fileName.textContent = selectedImage.name;

        const reader = new FileReader();

        reader.onload = function (event) {

            imagePreview.src = event.target.result;
            previewArea.hidden = false;

            previewMessage.textContent =
                "Preview only. Submit to save this demonstration case.";
        };

        reader.onerror = function () {

            alert("Could not preview the selected image.");

            previewArea.hidden = true;
        };

        reader.readAsDataURL(selectedImage);
    });


    // ==========================================
    // 4. SUBMIT THE UPLOAD FORM
    // ==========================================

    uploadForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        if (submitButton.disabled) {
            return;
        }

        const patientId = patientIdInput.value.trim();
        const patientAge = patientAgeInput.value.trim();
        const patientGender = patientGenderInput.value;
        const bodyPart = bodyPartInput.value;

        // Validate patient ID.
        if (!patientId) {

            alert("Please enter a demo patient ID.");

            patientIdInput.focus();

            return;
        }

        // Validate age.
        const age = Number(patientAge);

        if (
            !patientAge ||
            !Number.isInteger(age) ||
            age < 1 ||
            age > 120
        ) {

            alert("Please enter a valid age between 1 and 120.");

            patientAgeInput.focus();

            return;
        }

        // Validate body part.
        if (bodyPart.toLowerCase() !== "chest") {

            alert(
                "RadiologyAI currently supports experimental " +
                "chest X-ray analysis only. Please select Chest."
            );

            bodyPartInput.focus();

            return;
        }

        // Validate selected image.
        if (!selectedImage || !xrayInput.files.length) {

            alert("Please select a chest X-ray image first.");

            xrayInput.focus();

            return;
        }

        // Get demonstration patient name.
        const patientName = prompt(
            "Enter a demo patient name:"
        );

        if (
            patientName === null ||
            !patientName.trim()
        ) {

            alert("Please enter a demo patient name.");

            return;
        }

        // ==========================================
        // 5. PREPARE FORM DATA
        // ==========================================

        const formData = new FormData();

        // These names must match app.py.
        formData.append(
            "patientName",
            patientName.trim()
        );

        formData.append(
            "patientId",
            patientId
        );

        formData.append(
            "age",
            patientAge
        );

        formData.append(
            "gender",
            patientGender
        );

        formData.append(
            "bodyPart",
            bodyPart.toLowerCase()
        );

        formData.append(
            "xrayImage",
            selectedImage
        );

        // ==========================================
        // 6. SEND REQUEST TO FLASK
        // ==========================================

        const originalButtonText = submitButton.textContent;

        submitButton.disabled = true;

        submitButton.textContent = "Saving case...";

        try {

            console.log(
                "RadiologyAI: Sending upload request."
            );

            const response = await fetch("/save_case", {
                method: "POST",
                body: formData
            });

            console.log(
                "RadiologyAI: HTTP status:",
                response.status
            );

            // Read the response.
            const responseText = await response.text();

            let result;

            try {

                result = JSON.parse(responseText);

            } catch (parseError) {

                console.error(
                    "RadiologyAI: Unexpected server response:",
                    responseText
                );

                throw new Error(
                    "The server returned an unexpected response. " +
                    "Check the Flask terminal."
                );
            }

            console.log(
                "RadiologyAI: Server response:",
                result
            );

            // ==========================================
            // 7. HANDLE SERVER ERRORS
            // ==========================================

            if (!response.ok) {

                throw new Error(
                    result.message ||
                    result.error ||
                    "The server could not save this case."
                );
            }

            // app.py returns HTTP 200 on success.
            if (response.status !== 200) {

                throw new Error(
                    "Unexpected server status: " +
                    response.status
                );
            }

            if (result.success !== true) {

                throw new Error(
                    result.message ||
                    "The server did not confirm that the case was saved."
                );
            }

            // ==========================================
            // 8. CONFIRM SUCCESS
            // ==========================================

            previewMessage.textContent =
                "Case saved successfully. Opening dashboard...";

            alert(
                "Chest X-ray case saved successfully!\n\n" +
                "Patient ID: " + patientId +
                "\nOpening dashboard..."
            );

            // Redirect to the dashboard.
            window.location.replace("/dashboard");

        } catch (error) {

            console.error(
                "RadiologyAI upload error:",
                error
            );

            alert(
                "Could not complete the upload.\n\n" +
                error.message
            );

        } finally {

            submitButton.disabled = false;

            submitButton.textContent = originalButtonText;
        }
    });
}


// ==========================================
// 9. SCRIPT LOADED
// ==========================================

console.log(
    "RadiologyAI upload script loaded successfully."
);