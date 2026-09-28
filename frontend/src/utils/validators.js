/**
 * Email format validation (RFC 5322 compliant regex)
 */
export const isValidEmail = (email) => {
  if (!email) return false;
  const regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return regex.test(String(email).trim());
};

/**
 * Password strength validator with strict security requirements:
 * Minimum 8 characters, at least 1 uppercase, 1 lowercase, 1 number, and 1 special char.
 */
export const isValidPassword = (password) => {
  if (!password || typeof password !== 'string') return false;
  return (
    password.length >= 8 &&
    /[A-Z]/.test(password) &&
    /[a-z]/.test(password) &&
    /[0-9]/.test(password) &&
    /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)
  );
};

export const getPasswordStrengthDetails = (password) => {
  if (!password) {
    return { score: 0, label: '', color: 'bg-slate-200 dark:bg-slate-700', passed: [] };
  }
  const checks = [
    { label: 'At least 8 characters', valid: password.length >= 8 },
    { label: 'Contains uppercase letter (A-Z)', valid: /[A-Z]/.test(password) },
    { label: 'Contains lowercase letter (a-z)', valid: /[a-z]/.test(password) },
    { label: 'Contains a number (0-9)', valid: /[0-9]/.test(password) },
    { label: 'Contains special character (!@#$%^&*)', valid: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password) },
  ];

  const score = checks.filter(c => c.valid).length;
  let label = 'Weak';
  let color = 'bg-rose-500';

  if (score === 3) {
    label = 'Fair';
    color = 'bg-amber-500';
  } else if (score === 4) {
    label = 'Good';
    color = 'bg-blue-500';
  } else if (score === 5) {
    label = 'Strong';
    color = 'bg-emerald-500';
  }

  return { score, label, color, checks };
};

/**
 * Phone Number format validation (supports international, regional, and 10-15 digits)
 */
export const isValidPhone = (phone) => {
  if (!phone) return true; // Optional in some forms
  const clean = String(phone).replace(/[\s\-\(\)\+]/g, '');
  return clean.length >= 10 && clean.length <= 15 && /^\d+$/.test(clean);
};

/**
 * Serial Number format validation
 * Alphanumeric, hyphen, underscore, 4 to 32 characters
 */
export const isValidSerialNumber = (serial) => {
  if (!serial) return false;
  const regex = /^[A-Za-z0-9\-_]{4,32}$/;
  return regex.test(String(serial).trim());
};

/**
 * Currency amount validator
 */
export const isValidAmount = (amount, maxAmount = null) => {
  if (amount === null || amount === undefined || amount === '') return false;
  const num = Number(amount);
  if (isNaN(num) || num <= 0) return false;
  if (maxAmount !== null && maxAmount !== undefined && num > Number(maxAmount)) return false;
  return true;
};

/**
 * Date range validation
 */
export const isValidIncidentDate = (incidentDate, purchaseDate = null) => {
  if (!incidentDate) return { valid: false, message: 'Incident date is required' };
  const inc = new Date(incidentDate);
  const now = new Date();
  
  if (isNaN(inc.getTime())) {
    return { valid: false, message: 'Invalid date format' };
  }
  if (inc > now) {
    return { valid: false, message: 'Incident date cannot be in the future' };
  }
  if (purchaseDate) {
    const purch = new Date(purchaseDate);
    if (!isNaN(purch.getTime()) && inc < purch) {
      return { valid: false, message: 'Incident date cannot be earlier than purchase date' };
    }
  }
  return { valid: true, message: '' };
};

/**
 * Validate Claim Submission Step Data
 */
export const validateClaimStep = (step, data, selectedWarranty = null) => {
  const errors = {};

  if (step === 1) {
    if (!data.warranty_id) {
      errors.warranty_id = 'Please select a registered covered equipment warranty.';
    }
  } else if (step === 2) {
    if (!data.fault_type || data.fault_type.trim() === '') {
      errors.fault_type = 'Please select a primary fault category.';
    }
    if (!data.damage_type || data.damage_type.trim() === '') {
      errors.damage_type = 'Please select the nature of damage.';
    }
    
    const pDate = selectedWarranty?.purchase_date || selectedWarranty?.start_date;
    const dateCheck = isValidIncidentDate(data.fault_occurrence_date || data.incident_date, pDate);
    if (!dateCheck.valid) {
      errors.fault_occurrence_date = dateCheck.message;
    }

    if (!data.description || data.description.trim().length < 15) {
      errors.description = 'Please provide a detailed fault description (minimum 15 characters).';
    } else if (data.description.trim().length > 1000) {
      errors.description = 'Description cannot exceed 1,000 characters.';
    }

    const maxPrice = selectedWarranty?.purchase_price || selectedWarranty?.product?.purchase_price;
    if (data.claim_amount === undefined || data.claim_amount === '' || Number(data.claim_amount) <= 0) {
      errors.claim_amount = 'Claim amount must be greater than $0.00.';
    } else if (maxPrice && Number(data.claim_amount) > Number(maxPrice)) {
      errors.claim_amount = `Claim amount cannot exceed original purchase price ($${Number(maxPrice).toFixed(2)}).`;
    }
  } else if (step === 3) {
    if (!data.documents || data.documents.length === 0) {
      errors.documents = 'At least 1 supporting document (Purchase Receipt / Proof of Purchase) is required.';
    }
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};