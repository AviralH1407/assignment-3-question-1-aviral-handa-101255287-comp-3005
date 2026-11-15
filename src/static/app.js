// Helper function to display operation status or error messages on the page
function showStatus(message, isError = false) {
    const statusEl = document.getElementById("status-message");
    statusEl.textContent = (isError ? "Error: " : "Success: ") + message;
}

// 1. Fetch all students from backend (calls getAllStudents) and render table rows
async function loadStudents() {
    try {
        const response = await fetch("/api/students");
        const data = await response.json();

        if (!response.ok) {
            showStatus(data.message || "Failed to load students", true);
            return;
        }

        const tbody = document.getElementById("students-table-body");
        tbody.innerHTML = "";

        data.students.forEach((student) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${student.student_id}</td>
                <td>${student.first_name}</td>
                <td>${student.last_name}</td>
                <td>${student.email}</td>
                <td>${student.enrollment_date || ""}</td>
            `;
            tbody.appendChild(row);
        });
    } catch (err) {
        showStatus("Network error while fetching students.", true);
    }
}

// 2. Handle Add Student form submission (calls addStudent)
document.getElementById("add-student-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const payload = {
        first_name: document.getElementById("first_name").value,
        last_name: document.getElementById("last_name").value,
        email: document.getElementById("email").value,
        enrollment_date: document.getElementById("enrollment_date").value
    };

    try {
        const response = await fetch("/api/students", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await response.json();

        if (!response.ok) {
            showStatus(data.message, true);
            return;
        }

        showStatus(data.message);
        event.target.reset();
        loadStudents(); // Refresh table after insert
    } catch (err) {
        showStatus("Network error while adding student.", true);
    }
});

// 3. Handle Update Student Email form submission (calls updateStudentEmail)
document.getElementById("update-email-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const studentId = document.getElementById("update_student_id").value;
    const newEmail = document.getElementById("new_email").value;

    try {
        const response = await fetch(`/api/students/${studentId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ new_email: newEmail })
        });
        const data = await response.json();

        if (!response.ok) {
            showStatus(data.message, true);
            return;
        }

        showStatus(data.message);
        event.target.reset();
        loadStudents(); // Refresh table after update
    } catch (err) {
        showStatus("Network error while updating email.", true);
    }
});

// 4. Handle Delete Student form submission (calls deleteStudent)
document.getElementById("delete-student-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const studentId = document.getElementById("delete_student_id").value;

    try {
        const response = await fetch(`/api/students/${studentId}`, {
            method: "DELETE"
        });
        const data = await response.json();

        if (!response.ok) {
            showStatus(data.message, true);
            return;
        }

        showStatus(data.message);
        event.target.reset();
        loadStudents(); // Refresh table after delete
    } catch (err) {
        showStatus("Network error while deleting student.", true);
    }
});

// Load students automatically when the page opens
window.addEventListener("DOMContentLoaded", loadStudents);
