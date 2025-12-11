This project uses a custom Raspberry Pi scanning system to evaluate WiFi coverage, signal strength, and handover performance inside McDonnell Douglas Hall. Using a Raspberry Pi 3B+ with an Alfa monitor-mode WiFi adapter, we performed passive scans with aircrack-ng and processed the results using Python (pandas, matplotlib).

Across 952 survey points and 194,742 measurements, we detected 54 physical access points, 1,111 BSSIDs, and 142 SLU-users radios. The building showed 98.6% handover coverage and zero dead zones, with over 95% of locations reporting good-to-excellent signal strength.

The repository includes the scanning methodology, data-processing scripts, and project documentation. This work demonstrates how low-cost embedded hardware can deliver accurate, real-world WiFi infrastructure analysis.
