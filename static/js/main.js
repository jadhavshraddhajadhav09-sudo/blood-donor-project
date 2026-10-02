/* Main JavaScript file for Blood Donor Registry & Emergency Request System */

document.addEventListener('DOMContentLoaded', function() {
  console.log('Blood Donor System JS Loaded.');

  // Phone number numeric enforcement
  const phoneInputs = document.querySelectorAll('input[type="tel"], input[name="phone_number"], input[name="contact_phone"]');
  phoneInputs.forEach(input => {
    input.addEventListener('input', function(e) {
      this.value = this.value.replace(/\D/g, '').slice(0, 10);
    });
  });

  // Reveal Contact Phone Number Handler
  const showContactBtns = document.querySelectorAll('.btn-show-contact');
  showContactBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      const donorId = this.getAttribute('data-donor-id');
      const targetContainer = document.getElementById(`phone-container-${donorId}`);
      
      if (!donorId || !targetContainer) return;

      this.disabled = true;
      this.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Loading...';

      fetch(`/api/donor/${donorId}/contact`)
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            targetContainer.innerHTML = `
              <a href="tel:${data.phone_number}" class="btn btn-sm btn-success fw-bold px-3 shadow-sm text-nowrap">
                <i class="bi bi-telephone-fill me-1"></i> Call ${data.phone_number}
              </a>
            `;
          } else {
            alert('Failed to retrieve contact number.');
            this.disabled = false;
            this.innerHTML = '<i class="bi bi-telephone"></i> Show Contact';
          }
        })
        .catch(err => {
          console.error(err);
          alert('Network error retrieving contact details.');
          this.disabled = false;
          this.innerHTML = '<i class="bi bi-telephone"></i> Show Contact';
        });
    });
  });

  // Matching Donors Modal Handler for Emergency Requests
  const matchingModalEl = document.getElementById('matchingDonorsModal');
  if (matchingModalEl) {
    matchingModalEl.addEventListener('show.bs.modal', function(event) {
      const button = event.relatedTarget;
      const requestId = button.getAttribute('data-request-id');
      const patientName = button.getAttribute('data-patient-name');
      const bloodGroup = button.getAttribute('data-blood-group');

      const modalTitle = document.getElementById('modalPatientTitle');
      const modalBody = document.getElementById('matchingDonorsList');

      modalTitle.textContent = `Matching Donors for ${patientName} (${bloodGroup})`;
      modalBody.innerHTML = `
        <div class="text-center py-5">
          <div class="spinner-border text-danger" role="status"></div>
          <p class="mt-2 text-muted fw-semibold">Searching compatible available donors...</p>
        </div>
      `;

      fetch(`/api/request/${requestId}/matching-donors`)
        .then(res => res.json())
        .then(data => {
          if (!data.success || !data.matching_donors || data.matching_donors.length === 0) {
            modalBody.innerHTML = `
              <div class="alert alert-info text-center my-4">
                <i class="bi bi-info-circle fs-3 d-block mb-2"></i>
                Currently no registered eligible donors match blood group <strong>${bloodGroup}</strong> in the registry.
              </div>
            `;
            return;
          }

          let html = `
            <div class="alert alert-light border border-danger border-opacity-25 mb-3">
              <small class="text-secondary d-block">
                <i class="bi bi-check-circle-fill text-danger me-1"></i>
                Showing compatible blood donors (${data.compatible_groups.join(', ')}) sorted by locality.
              </small>
            </div>
            <div class="row g-3">
          `;

          data.matching_donors.forEach(donor => {
            const cityBadge = donor.is_same_city 
              ? '<span class="badge bg-success bg-opacity-10 text-success border border-success border-opacity-25"><i class="bi bi-geo-alt-fill me-1"></i>Same City</span>' 
              : `<span class="badge bg-secondary bg-opacity-10 text-secondary">${donor.city}</span>`;

            html += `
              <div class="col-md-6">
                <div class="card h-100 border-0 shadow-sm p-3 bg-white">
                  <div class="d-flex align-items-center justify-content-between mb-2">
                    <span class="blood-badge">${donor.blood_group}</span>
                    <div>${cityBadge}</div>
                  </div>
                  <h6 class="fw-bold mb-1">${donor.full_name}</h6>
                  <p class="text-muted small mb-2">
                    <i class="bi bi-geo-alt"></i> ${donor.area}, ${donor.city}<br>
                    <i class="bi bi-clock-history"></i> Last Donated: ${donor.last_donation_date}
                  </p>
                  <div id="modal-phone-container-${donor.id}" class="mt-auto pt-2">
                    <button class="btn btn-sm btn-outline-danger w-100 btn-modal-show-contact" data-donor-id="${donor.id}">
                      <i class="bi bi-telephone me-1"></i> Show Contact
                    </button>
                  </div>
                </div>
              </div>
            `;
          });

          html += '</div>';
          modalBody.innerHTML = html;

          // Attach handler for modal phone reveal
          document.querySelectorAll('.btn-modal-show-contact').forEach(b => {
            b.addEventListener('click', function() {
              const dId = this.getAttribute('data-donor-id');
              const container = document.getElementById(`modal-phone-container-${dId}`);
              this.disabled = true;
              this.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>';

              fetch(`/api/donor/${dId}/contact`)
                .then(r => r.json())
                .then(d => {
                  if (d.success) {
                    container.innerHTML = `
                      <a href="tel:${d.phone_number}" class="btn btn-sm btn-success w-100 fw-bold">
                        <i class="bi bi-telephone-fill me-1"></i> Call ${d.phone_number}
                      </a>
                    `;
                  }
                });
            });
          });
        })
        .catch(err => {
          console.error(err);
          modalBody.innerHTML = '<div class="alert alert-danger">Error loading donor information.</div>';
        });
    });
  }

  // Admin Dashboard Charts (if element exists)
  const chartCanvas = document.getElementById('bloodGroupChart');
  if (chartCanvas && typeof Chart !== 'undefined') {
    fetch('/admin/api/stats')
      .then(res => res.json())
      .then(data => {
        new Chart(chartCanvas, {
          type: 'bar',
          data: {
            labels: data.blood_groups,
            datasets: [{
              label: 'Registered Donors',
              data: data.donor_counts,
              backgroundColor: [
                '#dc3545', '#b02a37', '#e63946', '#d62828', 
                '#f77f00', '#003049', '#9d0208', '#6a040f'
              ],
              borderRadius: 8
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: { display: false },
              title: { display: true, text: 'Donor Distribution by Blood Group' }
            },
            scales: {
              y: {
                beginAtZero: true,
                ticks: { stepSize: 1 }
              }
            }
          }
        });
      });
  }
});
