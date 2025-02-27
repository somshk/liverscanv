const dropArea = document.querySelector(".upload-image-main");
const dropText = document.querySelector(".upload-image-text");
const input = document.querySelector("input[name='images']");
const dateField = document.querySelector(".date-now");
const noSelectedBanner = document.querySelector(".assigned-reports-report-details");
const selectedBanner = document.querySelector(".doctor-results-main");
const patientIDDiv = document.querySelector(".patient-id-value");
const statusDiv = document.querySelector(".status-value");
const initialDiagnosisDiv = document.querySelector(".diagnosis-value");
const finalDiagnosisDiv = document.querySelector(".final-diagnosis-value");
const remarksDiv = document.querySelector(".remarks");
const diagnosisDateDiv = document.querySelector(".date-value");
const areaDiv = document.querySelector(".area-value");
const today = new Date();
const year = today.getFullYear();
const month = String(today.getMonth() + 1).padStart(2, '0'); // Months are 0-indexed
const day = String(today.getDate()).padStart(2, '0');
const formattedDate = `${year}-${month}-${day}`;

if (dateField) {
    dateField.value = formattedDate;
}

document.addEventListener("DOMContentLoaded", () => {
    const searchBox = document.querySelector(".search-input");
    const searchItems = document.querySelectorAll(".search-items");

    searchBox.addEventListener("input", () => {
        const query = searchBox.value.toLowerCase();

        searchItems.forEach((item) => {
            const text = item.textContent.toLowerCase();
            const parentDiv = item.parentElement.parentElement;
            if (text.includes(query)) {
                parentDiv.style.display = "block";
            } else {
                parentDiv.style.display = "none";
            }
        });
    });
});


document.addEventListener("DOMContentLoaded", () => {
    const burgerIcon = document.querySelector(".burger-icon");
    const navbarMain = document.querySelector(".navbar-main");
    // Toggle the 'active' class on click
    burgerIcon.addEventListener("click", () => {
        navbarMain.classList.toggle("active");
    });
});

async function fetchData(link) {
    try {
        const response = await fetch(`/api/${link}/`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// Function to display diagnosis details below the card on mobile view
function displayDiagnosisDetailsMobile(diagnosisId, diagnosis_data) {
    const cardDiv = document.querySelector(`[data-id="${diagnosisId}"]`);

    // Remove existing mobile details div if it exists
    const existingDetailsDiv = document.querySelector(`.mobile-diagnosis-details[data-id="${diagnosisId}"]`);
    if (existingDetailsDiv) {
        existingDetailsDiv.remove();
    }

    cardDiv.classList.add('active-card');
    // Create a new div for mobile diagnosis details
    const detailsDiv = document.createElement('div');
    detailsDiv.classList.add('mobile-diagnosis-details');
    detailsDiv.setAttribute('data-id', diagnosisId);

    // Populate the details div
    detailsDiv.innerHTML = `
        <p><strong>Patient ID:</strong> ${diagnosis_data.patient_id}</p>
        <p><strong>Status:</strong> ${getStatusText(diagnosis_data.status)}</p>
        <p><strong>Initial Diagnosis:</strong> ${diagnosis_data.initial_diagnosis}</p>
        <p><strong>Final Diagnosis:</strong> ${diagnosis_data.final_diagnosis || 'N/A'}</p>
        <p><strong>Remarks:</strong> ${diagnosis_data.remarks || 'N/A'}</p>
        <p><strong>Diagnosis Date:</strong> ${diagnosis_data.diagnosis_date || 'N/A'}</p>
        <p><strong>Area:</strong> ${diagnosis_data.area ? `${diagnosis_data.area} cm\u00B2` : '0 cm\u00B2'}</p>
    `;

    // Insert the details div after the selected card div
    cardDiv.insertAdjacentElement('afterend', detailsDiv);
}

// Helper function to get status text
function getStatusText(status) {
    switch (status) {
        case 1:
            return 'Waiting for predictions';
        case 2:
            return 'Waiting for validation';
        case 3:
            return 'Finished';
        default:
            return 'Unknown status';
    }
}

async function fetchDiagnosisDetails(diagnosisId) {
    let diagnosis_data = await fetchData(`diagnoses/${diagnosisId}`);
    
    if (window.innerWidth <= 600) {
        // add logic for card diagnosis info display
        displayDiagnosisDetailsMobile(diagnosisId, diagnosis_data);
        return;
    }

    const allCards = document.querySelectorAll('.active-card');

    if (allCards){
        allCards.forEach((card) => {
            card.classList.remove('active-card');
        });
    }


    const cardDiv = document.querySelector(`[data-id="${diagnosisId}"]`);
    cardDiv.classList.add('active-card');

    if (diagnosis_data) {
        noSelectedBanner.style.display = "none";
        selectedBanner.style.display = "block";
        
        patientIDDiv.value = diagnosis_data.patient_id;
        
        statusDiv.textContent = getStatusText(diagnosis_data.status);
        initialDiagnosisDiv.textContent = diagnosis_data.initial_diagnosis;

        if (finalDiagnosisDiv) {
            finalDiagnosisDiv.textContent = diagnosis_data.final_diagnosis || "";
        }
        
        remarksDiv.textContent = diagnosis_data.remarks || "";
        diagnosisDateDiv.textContent = diagnosis_data.diagnosis_date || "";

        if (diagnosis_data.initial_diagnosis == 'normal' || diagnosis_data.initial_diagnosis == null) {
            areaDiv.textContent = `0 cm\u00B2`;
        } else {
            areaDiv.textContent = `${diagnosis_data.area} cm\u00B2`;
        }

        const unenhanced_img = document.querySelector('img[alt="unenhanced"]')
        unenhanced_img.src = diagnosis_data.proxy_unenhanced_ct
        const arterial_img = document.querySelector('img[alt="arterial"]')
        arterial_img.src = diagnosis_data.proxy_arterial_ct
        const portal_venous_img = document.querySelector('img[alt="portal venous"]')
        portal_venous_img.src = diagnosis_data.proxy_portal_venous_ct
        
        console.log(diagnosis_data);

    } else {
        console.error('No data found for the given diagnosis ID.');
        noSelectedBanner.style.display = "block"; // Show no selected banner if no data
        selectedBanner.style.display = "none"; // Hide the selected banner
    }
}

let files = [];


dropArea.onclick = () => input.click();

input.addEventListener("change", function() {
    files = Array.from(this.files); // Update files array
    showImages();
});

dropArea.addEventListener("dragover", (event) => {
    event.preventDefault();
    dropArea.classList.add("active-image");
    dropText.textContent = "Release to Upload files";
});

dropArea.addEventListener("dragleave", () => {
    dropArea.classList.remove("active-image");
    dropText.textContent = "Drag and drop images or click to upload";
});

dropArea.addEventListener("drop", (event) => {
    event.preventDefault();
    dropArea.classList.remove("active-image");
    let droppedFiles = Array.from(event.dataTransfer.files);
    files = [...files, ...droppedFiles]; // Merge new and existing files
    showImages();
});

function showImages() {
    let validTypes = ["image/jpeg", "image/jpg", "image/png"];
    dropArea.innerHTML = "";

    if (files.length > 3) {
        alert("You can only upload up to 3 images.");
        files = [];
        return;
    }

    for (let file of files) {
        if (validTypes.includes(file.type)) {
            let fileReader = new FileReader();
            fileReader.onload = () => {
                let fileURL = fileReader.result;
                let imgTag = `<img src="${fileURL}" alt="">`;
                dropArea.innerHTML += imgTag;
            };
            fileReader.readAsDataURL(file);
        } else {
            alert("It must be an image file.");
            files = [];
            dropArea.innerHTML = "";
            return;
        }
    }
}

const form = document.querySelector(".create_request_form");

// Handle form submission
form.addEventListener("submit", function (event) {
    event.preventDefault();

    let formData = new FormData(form); // Automatically includes all fields

    // Append images properly
    files.forEach((file) => {
        formData.append("images", file);
    });

    // Show the loading spinner
    let spinner = document.getElementById("loading-spinner");
    spinner.style.display = "flex";

    fetch('/doctor/upload', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken') // Ensure CSRF token is included
        }
    })
    .then(response => response.json())  // Expect JSON response
    .then(data => {
        spinner.style.display = "none";
        if (data.success) {
            alert(data.message);  // Show alert on success
            setTimeout(() => {
                window.location.reload();  // Reload after 1 second
            }, 1000);
        } else {
            alert("Error: " + data.errors.join("\n"));  // Show errors
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("An unexpected error occurred. Please try again.");
    });
});

// CSRF Token helper function
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}