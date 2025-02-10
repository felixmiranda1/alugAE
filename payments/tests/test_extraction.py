import os
from payments.services.receipt_extractor import PixReceiptExtractor

# Path to the test receipt (modify this based on your actual path)
TEST_RECEIPT_PATH = "/Users/felixmiranda/alugAE/comprovante2.jpeg"  # Replace with your file path

def test_receipt_extraction():
    """
    Tests the extraction of data from a PIX receipt.
    """
    if not os.path.exists(TEST_RECEIPT_PATH):
        print(f"File {TEST_RECEIPT_PATH} not found. Please provide a valid test file.")
        return

    extracted_data = PixReceiptExtractor.process_receipt(TEST_RECEIPT_PATH)

    print("\n🔍 Extracted Data:")
    for key, value in extracted_data.items():
        print(f"{key}: {value}")

# Run the test
if __name__ == "__main__":
    test_receipt_extraction()
