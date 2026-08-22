import { Bell, LineChart, PiggyBank } from 'lucide-react'

const FEATURES = [
  {
    icon: LineChart,
    title: 'Track Prices',
    description: 'Add products from your favorite stores and let DealDrop monitor their prices.',
  },
  {
    icon: Bell,
    title: 'Catch the Drop',
    description: 'Know when the price falls so you can buy at the right moment.',
  },
  {
    icon: PiggyBank,
    title: 'Save Money',
    description: 'Stop overpaying. DealDrop helps you find the best time to purchase.',
  },
]

export default function FeatureSection({ onOpenSignUp }) {
  return (
    <>
      <section className="features">
        {FEATURES.map(({ icon: Icon, title, description }) => (
          <div className="feature-card" key={title}>
            <span className="feature-icon">
              <Icon size={20} />
            </span>
            <h3 className="feature-title">{title}</h3>
            <p className="feature-description">{description}</p>
          </div>
        ))}
      </section>

      <section className="cta">
        <h2 className="cta-heading">Ready to stop overpaying?</h2>
        <p className="cta-subtext">Start tracking your favorite products today.</p>
        <button type="button" className="btn btn-primary cta-btn" onClick={onOpenSignUp}>
          Create Free Account
        </button>
      </section>
    </>
  )
}
