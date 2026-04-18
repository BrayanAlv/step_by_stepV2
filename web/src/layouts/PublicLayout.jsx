import React from 'react';

export default function PublicLayout({ children }){
  return (
    <div className="min-h-screen bg-[var(--color-neutral-bg)]">
      <main className="max-w-5xl mx-auto p-6">{children}</main>
    </div>
  );
}
