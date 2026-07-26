/* Dynamic Appointment Booking Wizard Handler */

document.addEventListener('DOMContentLoaded', () => {
    const hospSelect = document.getElementById('booking_hospital_id');
    const deptSelect = document.getElementById('booking_department_id');
    const docSelect = document.getElementById('booking_doctor_id');
    const dateInput = document.getElementById('booking_date');
    const slotContainer = document.getElementById('slots_grid_container');
    const selectedSlotInput = document.getElementById('selected_time_slot');
    const feeDisplay = document.getElementById('consultation_fee_display');
    const tokenPreview = document.getElementById('token_preview_box');
    const aiSlotBtn = document.getElementById('ai_recommend_slot_btn');

    if (hospSelect && deptSelect) {
        hospSelect.addEventListener('change', updateDoctors);
        deptSelect.addEventListener('change', updateDoctors);
    }

    if (docSelect) {
        docSelect.addEventListener('change', () => {
            fetchTimeSlots();
            updateDoctorFee();
        });
    }

    if (dateInput) {
        // Set minimum date to today
        const today = new Date().toISOString().split('T')[0];
        dateInput.min = today;
        if (!dateInput.value) dateInput.value = today;
        
        dateInput.addEventListener('change', fetchTimeSlots);
    }

    if (aiSlotBtn) {
        aiSlotBtn.addEventListener('click', async () => {
            const docId = docSelect ? docSelect.value : null;
            if (!docId) {
                showToast('Please select a hospital and doctor first.', 'warning');
                return;
            }

            try {
                const res = await fetch('/ai/recommend-slot', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ doctor_id: docId, preferred_time: 'morning' })
                });
                const data = await res.json();

                if (data.recommended_slot) {
                    highlightSlot(data.recommended_slot);
                    showToast(`AI Recommended Slot: ${data.recommended_slot}`, 'success');
                }
            } catch (e) {
                console.error(e);
            }
        });
    }

    async function updateDoctors() {
        const hospId = hospSelect.value;
        const deptId = deptSelect.value;
        
        if (!hospId) return;

        docSelect.innerHTML = '<option value="">-- Loading Doctors... --</option>';

        let url = `/api/doctors?hospital_id=${hospId}`;
        if (deptId) url += `&department_id=${deptId}`;

        try {
            const res = await fetch(url);
            const doctors = await res.json();

            docSelect.innerHTML = '<option value="">-- Select Doctor --</option>';
            if (doctors.length === 0) {
                docSelect.innerHTML = '<option value="">No doctors available for this department</option>';
                return;
            }

            doctors.forEach(doc => {
                const opt = document.createElement('option');
                opt.value = doc.id;
                opt.textContent = `Dr. ${doc.name} (${doc.specialization}) - ₹${doc.consultation_fee}`;
                opt.dataset.fee = doc.consultation_fee;
                docSelect.appendChild(opt);
            });
        } catch (err) {
            console.error('Error fetching doctors:', err);
        }
    }

    function updateDoctorFee() {
        const selectedOpt = docSelect.options[docSelect.selectedIndex];
        if (selectedOpt && selectedOpt.dataset.fee) {
            if (feeDisplay) feeDisplay.textContent = `₹${parseFloat(selectedOpt.dataset.fee).toFixed(2)}`;
        }
    }

    async function fetchTimeSlots() {
        const docId = docSelect.value;
        const dateVal = dateInput.value;

        if (!docId || !dateVal || !slotContainer) return;

        slotContainer.innerHTML = '<div class="skeleton" style="height: 60px; width: 100%;"></div>';

        try {
            const res = await fetch(`/api/doctor/${docId}/slots?date=${dateVal}`);
            const data = await res.json();

            slotContainer.innerHTML = '';
            if (!data.slots || data.slots.length === 0) {
                slotContainer.innerHTML = '<p class="text-muted">No time slots configured.</p>';
                return;
            }

            data.slots.forEach(s => {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = `btn btn-sm ${s.is_available ? 'btn-outline' : 'btn-secondary'}`;
                btn.textContent = s.slot;
                btn.disabled = !s.is_available;

                if (s.is_available) {
                    btn.addEventListener('click', () => {
                        document.querySelectorAll('#slots_grid_container button').forEach(b => b.classList.remove('btn-primary'));
                        btn.classList.remove('btn-outline');
                        btn.classList.add('btn-primary');
                        selectedSlotInput.value = s.slot;

                        if (tokenPreview) {
                            tokenPreview.style.display = 'block';
                        }
                    });
                } else {
                    btn.style.opacity = '0.5';
                    btn.title = 'Slot Booked';
                }

                slotContainer.appendChild(btn);
            });
        } catch (e) {
            console.error('Error loading slots:', e);
        }
    }

    function highlightSlot(slotTime) {
        const buttons = slotContainer.querySelectorAll('button');
        buttons.forEach(btn => {
            if (btn.textContent.trim() === slotTime.trim() && !btn.disabled) {
                btn.click();
            }
        });
    }
});
