import serial
import time
import statistics
import matplotlib.pyplot as plt

# Configuration
PORT = 'COM9'
BAUD = 115200 # Standard for ESP32 serial communication
SAMPLES = 10

def get_temperature(ser):
    """Reads one temperature point from the ESP32."""
    while True:
        line = ser.readline().decode('utf-8').strip()
        if "Temperature:" in line:
            try:
                # Extract float value after "Temperature: "
                temp_str = line.split(":")[1].split("C")[0].strip()
                return float(temp_str)
            except (ValueError, IndexError):
                continue

def run_experiment():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=2)
        print(f"Connected to {PORT} successfully.")
        time.sleep(2) # Wait for serial to stabilize
        
        # Phase 2A: Sequential Measurements (Natural Variation)
        print("\n--- PHASE 2A: SEQUENTIAL MEASUREMENTS (Natural Variation) ---")
        print("Gathering 10 samples with no changes...")
        seq_data = []
        for i in range(SAMPLES):
            temp = get_temperature(ser)
            seq_data.append(temp)
            print(f"Sample {i+1}: {temp:.2f} C")
            time.sleep(1)
            
        # Phase 2B: Randomized/Blocked Measurements (Induced Variation)
        print("\n--- PHASE 2B: RANDOMIZED/BLOCKED MEASUREMENTS (Induced Variation) ---")
        print("Prepare to induce variation (e.g., change operator, wait 5 min, or block heat).")
        blocked_data = []
        for i in range(SAMPLES):
            input(f"Press Enter to take sample {i+1} after inducing variation/block...")
            temp = get_temperature(ser)
            blocked_data.append(temp)
            print(f"Sample {i+1}: {temp:.2f} C")
        
        ser.close()
        
        # Statistics Calculation
        def calc_stats(data):
            mean_val = statistics.mean(data)
            var_val = statistics.variance(data)
            range_val = max(data) - min(data)
            return mean_val, var_val, range_val

        m1, v1, r1 = calc_stats(seq_data)
        m2, v2, r2 = calc_stats(blocked_data)
        
        print("\n" + "="*40)
        print("RESULTS SUMMARY")
        print("="*40)
        print(f"{'Metric':<15} | {'Sequential (Natural)':<20} | {'Blocked (Induced)':<20}")
        print("-" * 65)
        print(f"{'Mean':<15} | {m1:<20.4f} | {m2:<20.4f}")
        print(f"{'Variance':<15} | {v1:<20.4f} | {v2:<20.4f}")
        print(f"{'Range':<15} | {r1:<20.4f} | {r2:<20.4f}")
        print("="*40)
        
        # Comparison logic
        if v2 > v1:
            diff = (v2 / v1) if v1 != 0 else 0
            print(f"Insight: Induced variation increased variance by {diff:.2f}x.")
        else:
            print("Insight: Natural noise was dominant or induced variation was negligible.")

        # Plotting
        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        plt.plot(range(1, 11), seq_data, 'bo-', label='Natural')
        plt.title('Sequential Sequence')
        plt.xlabel('Sample #')
        plt.ylabel('Temp (C)')
        plt.grid(True)
        
        plt.subplot(1, 2, 2)
        plt.plot(range(1, 11), blocked_data, 'ro-', label='Induced')
        plt.title('Randomized/Blocked Sequence')
        plt.xlabel('Sample #')
        plt.ylabel('Temp (C)')
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig('variation_results.png')
        print("\nPlot saved as 'variation_results.png'.")
        plt.show()

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_experiment()
