import React from 'react';
import TopBottomPurchaseChart from './TopBottomPurchaseChart';

export default function TopBottomGrid({
  top = [],
  bottom = [],
}: {
  top?: Array<{ assetId: string; purchases: any[] }>;
  bottom?: Array<{ assetId: string; purchases: any[] }>;
}) {
  const items = [...(top || []), ...(bottom || [])].slice(0, 10);
  if (items.length === 0) return <div role="status">No charts to display.</div>;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 12 }}>
      {items.map((asset, i) => (
        <TopBottomPurchaseChart
          key={asset.assetId || i}
          title={asset.assetId || `asset-${i}`}
          data={asset.purchases?.map((p: any) => ({ timestamp: p.timestamp, price: p.price, amount: p.amount }))}
          width={360}
          height={220}
        />
      ))}
    </div>
  );
}
