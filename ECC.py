import csv
import random
from ecdsa import SigningKey, VerifyingKey, SECP256k1

def encrypt(curve, public_key, G, M, k=None):
    if k is None:
        k = random.randint(1, curve.order - 1)

    M_point = G * (M % curve.order)  # Convert M to a point on the curve

    public_key = VerifyingKey.from_pem(public_key)
    Q = public_key.pubkey.point  # Get the public key point

    C1 = G * k
    C2 = M_point + Q * k

    return C1, C2

def decrypt(curve, private_key, C1, C2):
    d = private_key.privkey.secret_multiplier
    M = C2 - C1 * d
    return M

def generate_keypair():
    private_key = SigningKey.generate(curve=SECP256k1)
    public_key = private_key.verifying_key
    return private_key, public_key

def encrypt_csv(curve, public_key, input_file, output_file):
    encrypted_successfully = []
    encrypted_failed = []

    G = curve.generator

    with open(input_file, 'r') as infile:
        reader = csv.reader(infile)
        rows = list(reader)

    for i, row in enumerate(rows):
        try:
            print(f"Processing row {i+1}: {row[:3]}")

            # Concatenate all values in the row
            combined_string = ''.join(row)
            combined_numeric = sum(int(col) for col in row if col.isdigit())
            ascii_sum = sum(ord(char) for char in combined_string if char.isalpha())

            M = combined_numeric + ascii_sum
            M_point = G * (M % curve.order)

            C1, C2 = encrypt(curve, public_key, G, M)

            encrypted_successfully.append([str(C1.x()), str(C1.y()), str(C2.x()), str(C2.y())])
            print(f"Encrypted data appended successfully: {[str(C1.x()), str(C1.y()), str(C2.x()), str(C2.y())]}")
        except Exception as e:
            print(f"Error processing row: {row}. Error: {str(e)}")
            encrypted_failed.append(row)

    print(f"\nTotal encrypted successfully: {len(encrypted_successfully)}")
    print(f"Total failed encryptions: {len(encrypted_failed)}")

    # Write only encrypted data to CSV
    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)

        # Write successful encrypted data
        for encrypted_row in encrypted_successfully:
            writer.writerow(encrypted_row)

        # Optionally, write failed rows as needed
        for failed_row in encrypted_failed:
            writer.writerow(["N/A", "N/A", "N/A", "N/A"])

curve = SECP256k1
private_key, public_key = generate_keypair()
print(f"Private key: {private_key.to_pem()}")
print(f"Public key: {public_key.to_pem()}")

input_file = 'path/to/your/data.csv'
output_file = 'path/to/encrypted_data.csv'
encrypt_csv(curve, public_key.to_pem(), input_file, output_file)
