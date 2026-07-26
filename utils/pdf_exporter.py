class ReceiptExporter:
    @staticmethod
    def generate_receipt_html(appointment, medical_note=None):
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Aura Health - Official Receipt & Smart Token</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; color: #1e293b; background: #f8fafc; }}
                .receipt-card {{ max-width: 750px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px rgba(0,0,0,0.05); overflow: hidden; }}
                .header {{ background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 25px 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 26px; font-weight: 700; letter-spacing: 0.5px; }}
                .header p {{ margin: 5px 0 0; opacity: 0.9; font-size: 14px; }}
                .content {{ padding: 30px; }}
                .token-box {{ text-align: center; background: #eff6ff; border: 2px dashed #3b82f6; padding: 20px; border-radius: 10px; margin-bottom: 25px; }}
                .token-label {{ font-size: 13px; text-transform: uppercase; color: #3b82f6; font-weight: 700; letter-spacing: 1px; }}
                .token-number {{ font-size: 34px; font-weight: 800; color: #1e3a8a; margin: 5px 0; }}
                .wait-info {{ font-size: 14px; color: #475569; margin-top: 5px; }}
                .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px; }}
                .field-group {{ margin-bottom: 12px; }}
                .label {{ font-size: 12px; text-transform: uppercase; color: #64748b; font-weight: 600; }}
                .value {{ font-size: 15px; font-weight: 600; color: #0f172a; margin-top: 3px; }}
                .prescription-section {{ background: #f1f5f9; padding: 20px; border-radius: 8px; margin-top: 20px; }}
                .prescription-section h3 {{ margin-top: 0; color: #1e3a8a; border-bottom: 2px solid #cbd5e1; padding-bottom: 8px; }}
                .footer {{ text-align: center; padding: 20px; border-top: 1px solid #e2e8f0; font-size: 12px; color: #94a3b8; background: #fafafa; }}
                @media print {{
                    body {{ background: white; padding: 0; }}
                    .receipt-card {{ border: none; box-shadow: none; }}
                    .no-print {{ display: none; }}
                }}
            </style>
        </head>
        <body>
            <div class="receipt-card">
                <div class="header">
                    <h1>{appointment['hospital_name']}</h1>
                    <p>{appointment['hospital_address']} | Contact: {appointment['hospital_phone']}</p>
                </div>
                <div class="content">
                    <div class="token-box">
                        <div class="token-label">Smart Appointment Token</div>
                        <div class="token-number">{appointment['token_number']}</div>
                        <div class="wait-info">Queue Position: #{appointment['queue_position']} | Estimated Wait Time: ~{appointment['predicted_wait_time']} mins</div>
                    </div>
                    
                    <div class="grid">
                        <div>
                            <div class="field-group">
                                <div class="label">Appointment ID</div>
                                <div class="value">{appointment['appointment_number']}</div>
                            </div>
                            <div class="field-group">
                                <div class="label">Patient Name</div>
                                <div class="value">{appointment['patient_name']} ({appointment['patient_age']} yrs, {appointment['patient_gender']})</div>
                            </div>
                            <div class="field-group">
                                <div class="label">Phone / Email</div>
                                <div class="value">{appointment['patient_phone']}</div>
                            </div>
                        </div>
                        <div>
                            <div class="field-group">
                                <div class="label">Doctor</div>
                                <div class="value">Dr. {appointment['doctor_name']} ({appointment['doctor_specialization']})</div>
                            </div>
                            <div class="field-group">
                                <div class="label">Department</div>
                                <div class="value">{appointment['department_name']}</div>
                            </div>
                            <div class="field-group">
                                <div class="label">Date & Time Slot</div>
                                <div class="value">{appointment['appointment_date']} at {appointment['time_slot']}</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="grid" style="border-top: 1px solid #e2e8f0; padding-top: 15px;">
                        <div>
                            <div class="label">Consultation Fee</div>
                            <div class="value">₹{appointment['consultation_fee']:,.2f}</div>
                        </div>
                        <div>
                            <div class="label">Payment Status</div>
                            <div class="value" style="color: #16a34a;">✔ {appointment['payment_status']}</div>
                        </div>
                    </div>
        """
        
        if medical_note:
            html += f"""
                    <div class="prescription-section">
                        <h3>Rx - Official Medical Prescription</h3>
                        <p><strong>Diagnosis:</strong> {medical_note['diagnosis']}</p>
                        <p><strong>Prescribed Medicines:</strong><br>{medical_note['prescription'].replace('\n', '<br>')}</p>
                        {"<p><strong>Lab Tests:</strong> " + medical_note['lab_tests'] + "</p>" if medical_note['lab_tests'] else ""}
                        {"<p><strong>Follow-Up Date:</strong> " + medical_note['follow_up_date'] + "</p>" if medical_note['follow_up_date'] else ""}
                    </div>
            """

        html += """
                    <div class="no-print" style="text-align: center; margin-top: 25px;">
                        <button onclick="window.print()" style="background: #2563eb; color: white; border: none; padding: 12px 25px; font-weight: 600; border-radius: 6px; cursor: pointer;">🖨 Print / Save PDF Receipt</button>
                    </div>
                </div>
                <div class="footer">
                    Aura Health Network • Powered by AI Smart Queue System • Keep this token for hospital entry
                </div>
            </div>
        </body>
        </html>
        """
        return html
