import React, { useState, useEffect } from 'react';
import { Card, Form } from 'react-bootstrap';

interface BillingFormProps {
  billingName: string;
  billingNif: string;
  billingAddress: string;
  onChange: (data: {
    billingName: string;
    billingNif: string;
    billingAddress: string;
  }) => void;
}

const BillingForm: React.FC<BillingFormProps> = ({
  billingName,
  billingNif,
  billingAddress,
  onChange,
}) => {
  const [localBillingName, setLocalBillingName] = useState(billingName);
  const [localBillingNif, setLocalBillingNif] = useState(billingNif);
  const [localBillingAddress, setLocalBillingAddress] = useState(billingAddress);

  useEffect(() => {
    setLocalBillingName(billingName);
    setLocalBillingNif(billingNif);
    setLocalBillingAddress(billingAddress);
  }, [billingName, billingNif, billingAddress]);

  const handleChange = (field: 'billingName' | 'billingNif' | 'billingAddress', value: string) => {
    const updatedData = {
      billingName: field === 'billingName' ? value : localBillingName,
      billingNif: field === 'billingNif' ? value : localBillingNif,
      billingAddress: field === 'billingAddress' ? value : localBillingAddress,
    };

    if (field === 'billingName') setLocalBillingName(value);
    if (field === 'billingNif') setLocalBillingNif(value);
    if (field === 'billingAddress') setLocalBillingAddress(value);

    onChange(updatedData);
  };

  return (
    <Card className="mb-4">
      <Card.Body>
        <h5 className="mb-3">Datos de Facturación</h5>

        <Form>
          <Form.Group className="mb-3">
            <Form.Label>Nombre / Razón Social *</Form.Label>
            <Form.Control
              type="text"
              value={localBillingName}
              onChange={(e) => handleChange('billingName', e.target.value)}
              placeholder="Nombre completo o razón social"
              required
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>NIF / CIF *</Form.Label>
            <Form.Control
              type="text"
              value={localBillingNif}
              onChange={(e) => handleChange('billingNif', e.target.value)}
              placeholder="12345678A o B12345678"
              required
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Dirección Completa *</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              value={localBillingAddress}
              onChange={(e) => handleChange('billingAddress', e.target.value)}
              placeholder="Calle, número, código postal, ciudad, provincia"
              required
            />
          </Form.Group>
        </Form>
      </Card.Body>
    </Card>
  );
};

export default BillingForm;
