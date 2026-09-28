import React from 'react';
import Badge from '../common/Badge';

export const StatusBadge = ({ status, size = 'md' }) => {
  return <Badge type="status" value={status} size={size} />;
};

export default StatusBadge;