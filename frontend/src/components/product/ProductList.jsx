import React, { useState, useMemo } from 'react';
import ProductCard from './ProductCard';
import Table from '../common/Table';
import { formatCurrency } from '../../utils/formatters';
import { LayoutGrid, List, Plus, Edit, Trash2 } from 'lucide-react';

export const ProductList = ({
  products = [],
  onSelectProduct = null,
  selectedProductId = null,
  onEditProduct = null,
  onDeleteProduct = null,
  isAdmin = false,
  onAddNew = null,
}) => {
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'table'
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [brandFilter, setBrandFilter] = useState('ALL');
  const [warrantyFilter, setWarrantyFilter] = useState('ALL');

  const uniqueBrands = useMemo(() => {
    const brands = products.map(p => p.brand).filter(Boolean);
    return [...new Set(brands)].sort();
  }, [products]);

  const filtered = products.filter((p) => {
    if (categoryFilter !== 'ALL' && p.category !== categoryFilter) return false;
    if (brandFilter !== 'ALL' && p.brand !== brandFilter) return false;
    if (warrantyFilter !== 'ALL') {
      const isExtended = p.warranty_months > 12;
      if (warrantyFilter === 'STANDARD' && isExtended) return false;
      if (warrantyFilter === 'EXTENDED' && !isExtended) return false;
    }
    return true;
  });

  const columns = [
    {
      key: 'model_name',
      label: 'Product / Model',
      sortable: true,
      render: (_, row) => (
        <div>
          <div className="font-semibold text-slate-900 dark:text-white">
            {row.brand} {row.model_name}
          </div>
          <div className="text-xs text-slate-400">{row.serial_prefix || 'No prefix'}</div>
        </div>
      ),
    },
    {
      key: 'category',
      label: 'Category',
      sortable: true,
      render: (val) => (
        <span className="text-xs font-medium px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
          {val?.replace(/_/g, ' ')}
        </span>
      ),
    },
    {
      key: 'msrp',
      label: 'MSRP',
      sortable: true,
      render: (val) => <span className="font-semibold">{formatCurrency(val)}</span>,
    },
    {
      key: 'warranty_months',
      label: 'Warranty',
      sortable: true,
      render: (val) => <span>{val} Months</span>,
    },
    ...(isAdmin
      ? [
          {
            key: 'actions',
            label: 'Actions',
            align: 'right',
            render: (_, row) => (
              <div className="flex items-center justify-end gap-2" onClick={(e) => e.stopPropagation()}>
                {onEditProduct && (
                  <button
                    type="button"
                    onClick={() => onEditProduct(row)}
                    className="p-1.5 text-slate-500 hover:text-brand-600 dark:hover:text-brand-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                )}
                {onDeleteProduct && (
                  <button
                    type="button"
                    onClick={() => onDeleteProduct(row)}
                    className="p-1.5 text-slate-500 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            ),
          },
        ]
      : []),
  ];

  return (
    <div className="space-y-4">
      {/* Controls Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="text-xs font-semibold px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 dark:text-white transition-shadow"
          >
            <option value="ALL">All Categories</option>
            <option value="ELECTRONICS">Consumer Electronics</option>
            <option value="HOME_APPLIANCES">Home Appliances</option>
            <option value="MOBILE_PHONES">Mobile Phones & Tablets</option>
            <option value="LAPTOPS">Laptops & Computers</option>
            <option value="AUDIO">Audio & Headphones</option>
            <option value="CAMERAS">Cameras & Photography</option>
            <option value="GAMING">Gaming & Consoles</option>
            <option value="WEARABLES">Smartwatches & Wearables</option>
            <option value="NETWORKING">Networking & Routers</option>
            <option value="PRINTERS">Printers & Scanners</option>
            <option value="KITCHEN">Kitchen Appliances</option>
            <option value="POWER_TOOLS">Power Tools & Equipment</option>
          </select>
          <select
            value={brandFilter}
            onChange={(e) => setBrandFilter(e.target.value)}
            className="text-xs font-semibold px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 dark:text-white transition-shadow"
          >
            <option value="ALL">All Brands</option>
            {uniqueBrands.map(brand => (
              <option key={brand} value={brand}>{brand}</option>
            ))}
          </select>
          <select
            value={warrantyFilter}
            onChange={(e) => setWarrantyFilter(e.target.value)}
            className="text-xs font-semibold px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 dark:text-white transition-shadow"
          >
            <option value="ALL">All Warranties</option>
            <option value="STANDARD">Standard (≤ 12mo)</option>
            <option value="EXTENDED">Extended (&gt; 12mo)</option>
          </select>
        </div>

        <div className="flex items-center gap-2 self-start md:self-auto">
          {onAddNew && (
            <button
              type="button"
              onClick={onAddNew}
              className="flex items-center gap-1.5 px-3.5 py-2 bg-brand-600 hover:bg-brand-500 text-white text-xs font-bold rounded-xl shadow-md shadow-brand-500/20 transition-all hover:-translate-y-0.5"
            >
              <Plus className="w-4 h-4" />
              Add Product
            </button>
          )}

          <div className="flex items-center bg-slate-100 dark:bg-slate-800 p-1 rounded-xl">
            <button
              type="button"
              onClick={() => setViewMode('grid')}
              className={`p-1.5 rounded-lg text-xs transition-all ${
                viewMode === 'grid'
                  ? 'bg-white dark:bg-slate-700 text-brand-600 dark:text-brand-400 shadow-sm'
                  : 'text-slate-500 hover:text-slate-900 dark:text-slate-400 hover:bg-white/50 dark:hover:bg-slate-700/50'
              }`}
            >
              <LayoutGrid className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={() => setViewMode('table')}
              className={`p-1.5 rounded-lg text-xs transition-all ${
                viewMode === 'table'
                  ? 'bg-white dark:bg-slate-700 text-brand-600 dark:text-brand-400 shadow-sm'
                  : 'text-slate-500 hover:text-slate-900 dark:text-slate-400 hover:bg-white/50 dark:hover:bg-slate-700/50'
              }`}
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Grid or Table View */}
      {viewMode === 'grid' ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
          {filtered.map((prod) => (
            <ProductCard
              key={prod.id}
              product={prod}
              isSelected={selectedProductId === prod.id}
              onSelect={onSelectProduct}
            />
          ))}
          {filtered.length === 0 && (
            <div className="col-span-full py-12 text-center text-sm text-slate-400 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800">
              No products found matching your filters.
            </div>
          )}
        </div>
      ) : (
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
          <Table
            columns={columns}
            data={filtered}
            searchKeys={['brand', 'model_name', 'category', 'serial_prefix']}
            onRowClick={onSelectProduct}
            emptyMessage="No products found matching your filters."
          />
        </div>
      )}
    </div>
  );
};

export default ProductList;