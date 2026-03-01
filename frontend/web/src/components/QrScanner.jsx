import { useEffect, useRef, useState } from 'react';
import { Html5Qrcode } from 'html5-qrcode';

const SCANNER_ID = 'organizer-qr-reader';

export default function QrScanner({ onScan, onError }) {
  const [active, setActive] = useState(false);
  const [cameraError, setCameraError] = useState(null);
  const scannerRef = useRef(null);

  const startScanning = async () => {
    setCameraError(null);
    try {
      const html5QrCode = new Html5Qrcode(SCANNER_ID);
      scannerRef.current = html5QrCode;
      await html5QrCode.start(
        { facingMode: 'environment' },
        { fps: 8, qrbox: { width: 250, height: 250 } },
        (decodedText) => {
          onScan(decodedText);
          stopScanning();
        },
        () => {}
      );
      setActive(true);
    } catch (err) {
      setCameraError(err?.message || 'Не удалось запустить камеру');
      if (onError) onError(err);
    }
  };

  const stopScanning = async () => {
    if (!scannerRef.current) return;
    try {
      await scannerRef.current.stop();
    } catch (_) {}
    scannerRef.current = null;
    setActive(false);
  };

  useEffect(() => {
    return () => {
      if (scannerRef.current) {
        scannerRef.current.stop().catch(() => {});
      }
    };
  }, []);

  return (
    <div className="qr-scanner-block">
      <div id={SCANNER_ID} className="qr-scanner-area" />
      {cameraError && <p className="page-text alert alert-error">{cameraError}</p>}
      <div className="qr-scanner-actions">
        {!active ? (
          <button type="button" className="btn primary" onClick={startScanning}>
            Включить камеру и сканировать QR
          </button>
        ) : (
          <button type="button" className="btn secondary" onClick={stopScanning}>
            Остановить сканирование
          </button>
        )}
      </div>
    </div>
  );
}
