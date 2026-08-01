using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using OpenCvSharp;
using EasyModbus; // ตัวอย่างใช้ EasyModbusClient สำหรับเชื่อมต่อ Modbus TCP PLC

class Program
{
    // --- CONFIGURATION ---
    static readonly int[] CamIndices = new int[] { 2, 3 }; // Index กล้อง Mechanic
    static readonly string BaseDir = @"D:\DEVELOPERS\test_cam\captured_images_csharp";
    
    static readonly string PlcIp = "192.168.1.50";
    static readonly int PlcPort = 502;
    static readonly int TriggerBitAddress = 0; // Address Bit จาก PLC

    static VideoCapture[] cap = new VideoCapture[CamIndices.Length];
    static string[] camDirs = new string[CamIndices.Length];

    static void Main(string[] args)
    {
        Console.WriteLine("=== C# Multi-Camera 4K & PLC Trigger System ===");

        // 1. สร้าง Subfolder แยกแต่ละกล้อง
        for (int i = 0; i < CamIndices.Length; i++)
        {
            camDirs[i] = Path.Combine(BaseDir, $"cam_{i + 1}");
            Directory.CreateDirectory(camDirs[i]);
        }

        // 2. Setup กล้องแต่ละตัวเป็น 4K + MJPEG
        for (int i = 0; i < CamIndices.Length; i++)
        {
            int idx = CamIndices[i];
            cap[i] = new VideoCapture(idx, VideoCaptureErrorCorrection.DirectShow);

            if (!cap[i].IsOpened())
            {
                Console.WriteLine($"Error: ไม่สามารถเปิดกล้อง Index {idx} ได้");
                return;
            }

            // ตั้งค่า Codec MJPG และ Resolution 4K
            cap[i].Set(VideoCaptureProperties.FourCC, VideoWriter.FourCC('M', 'J', 'P', 'G'));
            cap[i].Set(VideoCaptureProperties.FrameWidth, 3840);
            cap[i].Set(VideoCaptureProperties.FrameHeight, 2160);
            cap[i].Set(VideoCaptureProperties.Fps, 30);
            
            Console.WriteLine($"Camera {i + 1} (Index {idx}) Ready.");
        }

        // 3. เชื่อมต่อ PLC (Modbus TCP)
        ModbusClient plc = new ModbusClient(PlcIp, PlcPort);
        try
        {
            plc.Connect();
            Console.WriteLine($"Connected to PLC at {PlcIp}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"PLC Connection Failed: {ex.Message}");
        }

        Console.WriteLine("\n[Running] Waiting for PLC Trigger... (Press Ctrl+C to stop)");

        // 4. Main Polling Loop
        bool lastTrigger = false;
        while (true)
        {
            try
            {
                // อ่านค่า Trigger Bit จาก PLC ( address 0, count 1)
                bool[] coils = plc.ReadCoils(TriggerBitAddress, 1);
                bool currentTrigger = coils[0];

                // ตรวจจับ Rising Edge (จังหวะเปลี่ยนจาก False -> True)
                if (currentTrigger && !lastTrigger)
                {
                    string timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss_fff");
                    Console.WriteLine($"[{timestamp}] PLC Trigger Detected! Capturing...");

                    // ถ่ายและบันทึกภาพทุกกล้องพร้อมกัน (ขนานด้วย Task/Thread)
                    Parallel.For(0, CamIndices.Length, camIdx =>
                    {
                        using (Mat frame = new Mat())
                        {
                            if (cap[camIdx].Read(frame) && !frame.Empty())
                            {
                                string filePath = Path.Combine(camDirs[camIdx], $"Cam{camIdx + 1}_4K_{timestamp}.jpg");
                                Cv2.ImWrite(filePath, frame);
                                Console.WriteLine($" -> Saved: {filePath}");
                            }
                        }
                    });

                    // เคลียร์ Bit สั่ง PLC กลับเป็น False (0)
                    plc.WriteSingleCoil(TriggerBitAddress, false);
                    Console.WriteLine($"Cleared PLC Trigger Bit Address {TriggerBitAddress} to FALSE\n");
                }

                lastTrigger = currentTrigger;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Loop Error: {ex.Message}");
            }

            Thread.Sleep(10); // Polling ทุก 10ms
        }
    }
}