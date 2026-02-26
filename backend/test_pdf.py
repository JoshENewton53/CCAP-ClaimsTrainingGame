"""Test PDF generation"""
import sys
sys.path.append('.')

from pdf_generator import DeathCertificateGenerator

try:
    gen = DeathCertificateGenerator()
    policy_data = {
        'policy_holder': 'John Smith',
        'state': 'Florida',
        'death_date': '2024-01-15',
        'policy_effective_date': '2020-01-01'
    }
    
    pdf_bytes = gen.generate_certificate(policy_data, ['name_mismatch'])
    print(f"SUCCESS: Generated PDF with {len(pdf_bytes)} bytes")
    
    # Save to file for testing
    with open('test_cert.pdf', 'wb') as f:
        f.write(pdf_bytes)
    print("Saved to test_cert.pdf")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
