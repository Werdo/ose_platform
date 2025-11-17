import React, { useState, useEffect } from 'react';
import { Card, Form, Button, Table, InputGroup } from 'react-bootstrap';
import type { TicketItem } from '../services/api';

interface TicketFormProps {
  ticketNumber: string;
  date: string;
  items: TicketItem[];
  total: number;
  onChange: (data: {
    ticketNumber: string;
    date: string;
    items: TicketItem[];
    total: number;
  }) => void;
}

const TicketForm: React.FC<TicketFormProps> = ({
  ticketNumber,
  date,
  items,
  onChange,
}) => {
  const [localTicketNumber, setLocalTicketNumber] = useState(ticketNumber);
  const [localDate, setLocalDate] = useState(date);
  const [localItems, setLocalItems] = useState<TicketItem[]>(items);

  useEffect(() => {
    setLocalTicketNumber(ticketNumber);
    setLocalDate(date);
    setLocalItems(items.length > 0 ? items : [createEmptyItem()]);
  }, [ticketNumber, date, items]);

  const createEmptyItem = (): TicketItem => ({
    description: '',
    quantity: 1,
    unit_price: 0,
    total: 0,
  });

  const calculateTotal = (itemsList: TicketItem[]) => {
    return itemsList.reduce((sum, item) => sum + item.total, 0);
  };

  const handleItemChange = (index: number, field: keyof TicketItem, value: any) => {
    const updatedItems = [...localItems];
    updatedItems[index] = { ...updatedItems[index], [field]: value };

    // Recalculate item total if quantity or unit_price changed
    if (field === 'quantity' || field === 'unit_price') {
      updatedItems[index].total =
        updatedItems[index].quantity * updatedItems[index].unit_price;
    }

    setLocalItems(updatedItems);

    const newTotal = calculateTotal(updatedItems);
    onChange({
      ticketNumber: localTicketNumber,
      date: localDate,
      items: updatedItems,
      total: newTotal,
    });
  };

  const handleAddItem = () => {
    const updatedItems = [...localItems, createEmptyItem()];
    setLocalItems(updatedItems);
    onChange({
      ticketNumber: localTicketNumber,
      date: localDate,
      items: updatedItems,
      total: calculateTotal(updatedItems),
    });
  };

  const handleRemoveItem = (index: number) => {
    if (localItems.length === 1) return; // Keep at least one item

    const updatedItems = localItems.filter((_, i) => i !== index);
    setLocalItems(updatedItems);
    onChange({
      ticketNumber: localTicketNumber,
      date: localDate,
      items: updatedItems,
      total: calculateTotal(updatedItems),
    });
  };

  const handleTicketNumberChange = (value: string) => {
    setLocalTicketNumber(value);
    onChange({
      ticketNumber: value,
      date: localDate,
      items: localItems,
      total: calculateTotal(localItems),
    });
  };

  const handleDateChange = (value: string) => {
    setLocalDate(value);
    onChange({
      ticketNumber: localTicketNumber,
      date: value,
      items: localItems,
      total: calculateTotal(localItems),
    });
  };

  return (
    <Card className="mb-4">
      <Card.Body>
        <h5 className="mb-3">Datos del Ticket</h5>

        <Form>
          <div className="row mb-3">
            <div className="col-md-6">
              <Form.Group>
                <Form.Label>Número de Ticket *</Form.Label>
                <Form.Control
                  type="text"
                  value={localTicketNumber}
                  onChange={(e) => handleTicketNumberChange(e.target.value)}
                  placeholder="Ej: TK-2024-001"
                  required
                />
              </Form.Group>
            </div>
            <div className="col-md-6">
              <Form.Group>
                <Form.Label>Fecha *</Form.Label>
                <Form.Control
                  type="date"
                  value={localDate}
                  onChange={(e) => handleDateChange(e.target.value)}
                  required
                />
              </Form.Group>
            </div>
          </div>

          <div className="mb-3">
            <div className="d-flex justify-content-between align-items-center mb-2">
              <Form.Label className="mb-0">Productos *</Form.Label>
              <Button variant="outline-primary" size="sm" onClick={handleAddItem}>
                <i className="bi bi-plus-circle me-1"></i>
                Agregar Producto
              </Button>
            </div>

            <div className="table-responsive">
              <Table bordered hover>
                <thead className="table-light">
                  <tr>
                    <th style={{ width: '40%' }}>Descripción</th>
                    <th style={{ width: '15%' }}>Cantidad</th>
                    <th style={{ width: '20%' }}>Precio Unit.</th>
                    <th style={{ width: '20%' }}>Total</th>
                    <th style={{ width: '5%' }}></th>
                  </tr>
                </thead>
                <tbody>
                  {localItems.map((item, index) => (
                    <tr key={index}>
                      <td>
                        <Form.Control
                          type="text"
                          size="sm"
                          value={item.description}
                          onChange={(e) =>
                            handleItemChange(index, 'description', e.target.value)
                          }
                          placeholder="Nombre del producto"
                        />
                      </td>
                      <td>
                        <Form.Control
                          type="number"
                          size="sm"
                          min="1"
                          step="1"
                          value={item.quantity}
                          onChange={(e) =>
                            handleItemChange(index, 'quantity', parseFloat(e.target.value) || 1)
                          }
                        />
                      </td>
                      <td>
                        <InputGroup size="sm">
                          <Form.Control
                            type="number"
                            min="0"
                            step="0.01"
                            value={item.unit_price}
                            onChange={(e) =>
                              handleItemChange(index, 'unit_price', parseFloat(e.target.value) || 0)
                            }
                          />
                          <InputGroup.Text>€</InputGroup.Text>
                        </InputGroup>
                      </td>
                      <td>
                        <InputGroup size="sm">
                          <Form.Control
                            type="number"
                            value={item.total.toFixed(2)}
                            readOnly
                            disabled
                          />
                          <InputGroup.Text>€</InputGroup.Text>
                        </InputGroup>
                      </td>
                      <td className="text-center">
                        <Button
                          variant="link"
                          size="sm"
                          className="text-danger p-0"
                          onClick={() => handleRemoveItem(index)}
                          disabled={localItems.length === 1}
                        >
                          <i className="bi bi-trash"></i>
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr className="table-light fw-bold">
                    <td colSpan={3} className="text-end">TOTAL:</td>
                    <td colSpan={2}>{calculateTotal(localItems).toFixed(2)} €</td>
                  </tr>
                </tfoot>
              </Table>
            </div>
          </div>
        </Form>
      </Card.Body>
    </Card>
  );
};

export default TicketForm;
