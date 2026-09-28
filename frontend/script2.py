import re

with open('frontend/src/components/claim/ClaimWizard.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Cpu with Zap
content = content.replace('Cpu,', 'Zap,')
content = content.replace('<Cpu className="w-4 h-4" />', '<Zap className="w-5 h-5 fill-current" />')

btn_old = '''<button
              type="button"
              disabled={submitting}
              onClick={handleSubmit}
              className="flex items-center gap-2 px-7 py-3 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-500 rounded-xl shadow-lg shadow-emerald-500/25 transition-all disabled:opacity-50"
            >'''
btn_new = '''<button
              type="button"
              disabled={submitting}
              onClick={handleSubmit}
              className="flex items-center gap-2 px-7 py-3 text-sm font-bold text-white bg-gradient-to-r from-brand-600 to-brand-400 hover:from-brand-500 hover:to-brand-300 rounded-xl shadow-lg shadow-brand-500/25 transition-all disabled:opacity-50"
            >'''
content = content.replace(btn_old, btn_new)
content = content.replace('<span>Submit & Adjudicate Now</span>', '<span>Trigger AI Adjudication</span>')

content = content.replace(
    "{ num: 1, title: 'Product & Warranty', icon: Package }",
    "{ num: 1, title: 'Select Product & Warranty', icon: Package }"
)

# Step active / future colors
content = re.sub(
    r"'bg-emerald-500 text-white shadow-md shadow-emerald-500/20'",
    "'bg-brand-600 text-white shadow-md shadow-brand-500/20'",
    content
)
content = re.sub(
    r"'bg-emerald-500' : 'bg-slate-100 dark:bg-slate-800'",
    "'bg-brand-600' : 'bg-slate-100 dark:bg-slate-800'",
    content
)

# Animation wrapper
content = content.replace(
    '<div className="p-8 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-xl shadow-slate-200/50 dark:shadow-none min-h-[420px] flex flex-col justify-between">',
    '<div className="p-8 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-xl shadow-slate-200/50 dark:shadow-none min-h-[420px] flex flex-col justify-between overflow-hidden relative">\n        <div key={currentStep} className="w-full transition-all duration-500 transform translate-x-0 animate-fade-in">'
)

content = content.replace(
    '        {/* Wizard Controls Footer */}',
    '        </div>\n\n        {/* Wizard Controls Footer */}'
)

with open('frontend/src/components/claim/ClaimWizard.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
