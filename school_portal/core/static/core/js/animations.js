document.addEventListener("DOMContentLoaded", function () {
    const mobileMenu = document.getElementById("mobile-menu");
    const navLinks = document.querySelector(".nav-links");

    mobileMenu.addEventListener("click", function() {
        navLinks.classList.toggle("showing");
        mobileMenu.classList.toggle("active")
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const heading = document.getElementById("history-heading");
    const text = "Our History";
    let index = 0;

    function typeEffect() {
        if (index < text.length) {
            heading.textContent += text.charAt(index);
            index++;
            setTimeout(typeEffect, 150);
        }
    }

    typeEffect();
});

document.addEventListener("DOMContentLoaded", function () {
    const successMsg = document.getElementById("successMsg");
    if (successMsg) {
      setTimeout(() => {
        successMsg.classList.add("show");
      }, 100);
  
      setTimeout(() => {
        successMsg.classList.remove("show");
      }, 4000);
    }
  });

  

document.addEventListener('DOMContentLoaded', function () {
    const roleSelect = document.getElementById('role');
    const studentFields = document.getElementById('studentFields');
    const teacherFields = document.getElementById('teacherFields');
  
    function toggleFields() {
      const role = roleSelect.value;
      studentFields.style.display = role === 'student' ? 'block' : 'none';
      teacherFields.style.display = role === 'teacher' ? 'block' : 'none';
    }
  
    // Initialize on page load and listen for changes
    toggleFields();
    roleSelect.addEventListener('change', toggleFields);
  });
   


document.addEventListener("DOMContentLoaded", function () {
    flatpickr("input[name='dob']", {
      dateFormat: "Y-m-d",
      maxDate: "today",
      altInput: true,
      altFormat: "F j, Y",
      theme: "material_blue"
    });
  });
/*dashboard*/
function payWithPaystack() {
    let handler = PaystackPop.setup({
      key: 'pk_test_your_public_key',  // Replace with your public key
      email: "{{ request.user.email }}",
      amount: 500000, // amount in kobo = ₦5000
      currency: 'NGN',
      ref: '' + Math.floor(Math.random() * 1000000000 + 1),
      callback: function (response) {
        alert('Payment complete! Reference: ' + response.reference);
        // You can send this to your server to verify and record
      },
      onClose: function () {
        alert('Transaction was not completed.');
      },
    });
    handler.openIframe();
  }
  
// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;
      
      const targetElement = document.querySelector(targetId);
      if (targetElement) {
        window.scrollTo({
          top: targetElement.offsetTop - 80,
          behavior: 'smooth'
        });
      }
    });
  });
  
  // Payment button handler
  function payWithPaystack() {
    const handler = PaystackPop.setup({
      key: 'YOUR_PAYSTACK_PUBLIC_KEY', // Replace with your Paystack public key
      email: 'student@school.com', // Replace with student's email
      amount: 5000000, // Amount in kobo (50000 = ₦500)
      currency: 'NGN',
      ref: '' + Math.floor((Math.random() * 1000000000) + 1),
      callback: function(response) {
        alert('Payment complete! Reference: ' + response.reference);
        // You can add AJAX call to your server to verify payment
      },
      onClose: function() {
        alert('Payment window closed.');
      }
    });
    handler.openIframe();
  }
  
  // File upload preview
  document.querySelector('.file-upload').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function(event) {
        const img = document.querySelector('.profile img');
        if (img) {
          img.src = event.target.result;
          img.classList.add('uploaded');
        }
      };
      reader.readAsDataURL(file);
    }
  });
  
  // Add hover effect to cards
  document.querySelectorAll('.assignment-card, .note-link, .result-link').forEach(card => {
    card.addEventListener('mouseenter', function() {
      this.style.transition = 'all 0.3s ease';
    });
  });
  
  // Notification system (example)
  function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => {
        notification.remove();
      }, 300);
    }, 3000);
  }
  
  
  document.getElementById('id_profile_picture').addEventListener('change', function(e) {
    var fileName = e.target.files[0] ? e.target.files[0].name : 'No file chosen';
    document.getElementById('file-name').textContent = fileName;
});
document.getElementById('logout-button').addEventListener('click', function(e) {
    e.preventDefault(); // Prevent the default action (to stay on the same page)
    
    // Show a confirmation dialog
    const confirmation = confirm("Are you sure you want to log out?");
    
    if (confirmation) {
        // If yes, log the user out and redirect them to the home page (assuming you have a 'logout' view)
        window.location.href = "{% url 'logout' %}"; // Replace with your actual logout URL
    } else {
        // If no, stay on the dashboard
        return false;
    }
});

// for my registration
document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');

    form.addEventListener('submit', function (e) {
        const password1Input = form.querySelector('[name="password1"]');
        const password2Input = form.querySelector('[name="password2"]');
        const password1 = password1Input.value;
        const password2 = password2Input.value;

        password1Input.classList.remove('error-field');
        password2Input.classList.remove('error-field');

        if (password1 !== password2) {
            e.preventDefault();
            password1Input.classList.add('error-field');
            password2Input.classList.add('error-field');
            alert("Passwords do not match!");
        }
    });
});


document.addEventListener("DOMContentLoaded", function () {
    const roleSelect = document.getElementById("role");
    const studentFields = document.getElementById("studentFields");
    const teacherFields = document.getElementById("teacherFields");
    const studentClass = document.getElementById("id_student_class");
    const admissionNumber = document.querySelector('input[name="admission_number"]');
    const subjectField = document.querySelector('input[name="subject"]');

    function toggleFields() {
        const role = roleSelect.value;
        if (role === "student") {
          studentFields.style.display = "block";
          teacherFields.style.display = "none";

          studentClass.required = true;
          studentClass.disabled = false;

          admissionNumber.disabled = false;
          admissionNumber.required = true;
          admissionNumber.value = "";

          subjectField.disabled = true;
          subjectField.required = false;
          subjectField.value = "";

          
      } else if (role === "teacher") {
          studentFields.style.display = "none";
          teacherFields.style.display = "block";


          studentClass.required = false;
          studentClass.disabled = true;  
          studentClass.value = "";

          admissionNumber.disabled = true;
          admissionNumber.required = false;
          admissionNumber.value = ""; 

          subjectField.disabled = false;
          subjectField.required = true;

      } else {
          studentFields.style.display = "none";
          teacherFields.style.display = "none";

          studentClass.required = false;
          studentClass.disabled = true;

          admissionNumber.disabled = true;
          admissionNumber.required = false;

          subjectField.disabled = true;
          subjectField.required = false;
      }
  
        
    }

    roleSelect.addEventListener("change", toggleFields);
    toggleFields(); 
});
   

// teachers dashboard
document.addEventListener('DOMContentLoaded', function() {
  // Add any interactive functionality here
  const cards = document.querySelectorAll('.dashboard-card');
  
  cards.forEach(card => {
      card.addEventListener('click', function(e) {
          // Example: Add click animation
          this.style.transform = 'scale(0.98)';
          setTimeout(() => {
              this.style.transform = '';
          }, 200);
      });
  });
});

document.addEventListener('DOMContentLoaded', function () {
    // For grade upload class-student dropdown
    const classSelect = document.getElementById('id_student_class');
    const studentSelect = document.getElementById('id_student');

    if (classSelect && studentSelect) {
        console.log("Dropdown logic loaded ✅");

        classSelect.addEventListener('change', function () {
            const classId = this.value;
            console.log("Selected class ID:", classId);

            if (classId) {
                fetch(`/ajax/get-students/?class_id=${classId}`)
                    .then(response => response.json())
                    .then(data => {
                        console.log("Fetched students:", data.students);

                        studentSelect.innerHTML = '<option value="">---------</option>';
                        data.students.forEach(student => {
                            const option = document.createElement('option');
                            option.value = student.id;
                            option.textContent = student.name;
                            studentSelect.appendChild(option);
                        });
                    })
                    .catch(error => console.error("Fetch failed:", error));
            } else {
                studentSelect.innerHTML = '<option value="">Select a class first</option>';
            }
        });
    }

    // Optional: Add this only if you're using flatpickr
    // if (typeof flatpickr !== 'undefined') {
    //     flatpickr("#id_exam_date", { dateFormat: "Y-m-d" });
    // }
});
