import { useState, useEffect } from 'react';
import * as svc from '../services/adminService';

export function useMetrics() {
  const [metrics, setMetrics] = useState(null);
  useEffect(()=>{ svc.getMetrics().then(setMetrics); }, []);
  return metrics;
}