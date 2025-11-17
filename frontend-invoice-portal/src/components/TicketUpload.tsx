import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Card, Button, Alert, Spinner } from 'react-bootstrap';
import { scanTicketOCR } from '../services/api';
import type { OCRResult } from '../services/api';

interface TicketUploadProps {
  onScanComplete: (result: OCRResult, file: File) => void;
}

const TicketUpload: React.FC<TicketUploadProps> = ({ onScanComplete }) => {
  const [preview, setPreview] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const uploadedFile = acceptedFiles[0];
    if (uploadedFile) {
      setFile(uploadedFile);
      setError(null);

      // Create preview
      const reader = new FileReader();
      reader.onload = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(uploadedFile);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp']
    },
    maxFiles: 1,
    multiple: false
  });

  const handleScan = async () => {
    if (!file) {
      setError('Por favor, sube una imagen primero');
      return;
    }

    setIsScanning(true);
    setError(null);

    try {
      const result = await scanTicketOCR(file);
      onScanComplete(result, file);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al escanear el ticket. Por favor, intenta de nuevo.');
      console.error('Error scanning ticket:', err);
    } finally {
      setIsScanning(false);
    }
  };

  const handleClear = () => {
    setFile(null);
    setPreview(null);
    setError(null);
  };

  return (
    <Card className="mb-4">
      <Card.Body>
        <h5 className="mb-3">Subir Imagen del Ticket</h5>

        {!preview ? (
          <div
            {...getRootProps()}
            className={`border border-2 border-dashed rounded p-5 text-center ${
              isDragActive ? 'border-primary bg-light' : 'border-secondary'
            }`}
            style={{ cursor: 'pointer' }}
          >
            <input {...getInputProps()} />
            <i className="bi bi-cloud-upload fs-1 text-secondary d-block mb-3"></i>
            {isDragActive ? (
              <p className="mb-0">Suelta la imagen aquí...</p>
            ) : (
              <>
                <p className="mb-2">Arrastra y suelta una imagen del ticket aquí</p>
                <p className="text-muted small mb-0">o haz clic para seleccionar un archivo</p>
              </>
            )}
          </div>
        ) : (
          <div>
            <div className="text-center mb-3">
              <img
                src={preview}
                alt="Preview"
                className="img-fluid rounded shadow-sm"
                style={{ maxHeight: '400px' }}
              />
            </div>

            <div className="d-flex gap-2 justify-content-center">
              <Button
                variant="primary"
                onClick={handleScan}
                disabled={isScanning}
              >
                {isScanning ? (
                  <>
                    <Spinner
                      as="span"
                      animation="border"
                      size="sm"
                      role="status"
                      className="me-2"
                    />
                    Escaneando...
                  </>
                ) : (
                  <>
                    <i className="bi bi-upc-scan me-2"></i>
                    Escanear Ticket
                  </>
                )}
              </Button>
              <Button variant="outline-secondary" onClick={handleClear}>
                <i className="bi bi-x-circle me-2"></i>
                Cambiar Imagen
              </Button>
            </div>
          </div>
        )}

        {error && (
          <Alert variant="danger" className="mt-3 mb-0">
            <i className="bi bi-exclamation-triangle me-2"></i>
            {error}
          </Alert>
        )}
      </Card.Body>
    </Card>
  );
};

export default TicketUpload;
