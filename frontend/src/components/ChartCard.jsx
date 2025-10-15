import { Card, CardContent, Typography } from '@mui/material';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const COLORS = ['#2563EB', '#60A5FA', '#93C5FD', '#DBEAFE'];

function ChartCard({ title, data, type }) {
  // Transform data for Recharts
  const chartData = Object.entries(data).map(([name, value]) => ({
    name,
    value
  }));

  return (
    <Card 
      sx={{ 
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.12)'
      }}
    >
      <CardContent>
        <Typography 
          variant="h6" 
          sx={{ mb: 3, fontWeight: 600, color: '#1F2937' }}
        >
          {title}
        </Typography>
        
        <ResponsiveContainer width="100%" height={300}>
          {type === 'bar' ? (
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis 
                dataKey="name" 
                tick={{ fill: '#6B7280', fontSize: 12 }}
                angle={-15}
                textAnchor="end"
                height={80}
              />
              <YAxis tick={{ fill: '#6B7280', fontSize: 12 }} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'white',
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }}
              />
              <Legend wrapperStyle={{ fontSize: '14px', color: '#6B7280' }} />
              <Bar dataKey="value" fill="#2563EB" radius={[8, 8, 0, 0]} />
            </BarChart>
          ) : (
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#2563EB"
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'white',
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }}
              />
            </PieChart>
          )}
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

export default ChartCard;

