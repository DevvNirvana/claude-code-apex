# Ruby on Rails Guidelines

## Convention Over Configuration
Rails has strong conventions. Follow them — don't fight them.

```
app/
├── controllers/     # Thin — delegate to models/services
├── models/          # Business logic, validations, associations
├── views/           # Presentation only — no logic
├── services/        # Complex multi-model operations
├── serializers/     # API response shaping
└── jobs/            # Background work (Sidekiq/ActiveJob)
```

## Models — Keep Fat, Controllers Thin
```ruby
class User < ApplicationRecord
  # Associations
  has_many :posts, dependent: :destroy
  has_one :profile, dependent: :destroy
  belongs_to :team, optional: true

  # Validations
  validates :email, presence: true, uniqueness: { case_sensitive: false }, format: { with: URI::MailTo::EMAIL_REGEXP }
  validates :name, presence: true, length: { maximum: 100 }

  # Scopes
  scope :active, -> { where(deactivated_at: nil) }
  scope :recent, -> { order(created_at: :desc) }
  scope :with_posts, -> { includes(:posts) }

  # Never expose sensitive attributes
  def as_json(options = {})
    super(options.merge(except: [:password_digest, :remember_token]))
  end
end
```

## N+1 Prevention (Rails-specific)
```ruby
# WRONG — N+1
@users = User.all
@users.each { |u| puts u.posts.count }  # N+1

# CORRECT
@users = User.includes(:posts).all

# Counter cache for counts
belongs_to :user, counter_cache: true
# Adds users.posts_count column, maintained automatically

# Bullet gem catches N+1 in development
gem 'bullet', group: :development
```

## Service Objects (for complex operations)
```ruby
# app/services/user_registration_service.rb
class UserRegistrationService
  def initialize(params)
    @params = params
  end

  def call
    ActiveRecord::Base.transaction do
      user = User.create!(@params.slice(:email, :name, :password))
      Profile.create!(user: user)
      WelcomeMailer.with(user: user).welcome_email.deliver_later
      user
    end
  rescue ActiveRecord::RecordInvalid => e
    { error: e.message }
  end
end

# In controller — stays thin
def create
  result = UserRegistrationService.new(user_params).call
  result.is_a?(User) ? redirect_to root_path : render :new
end
```

## Migrations
- Always add indices on foreign keys and columns used in WHERE/ORDER
- Use `add_column` + `change_column_default` instead of directly setting defaults
- Never delete migrations — mark deprecated and create new ones
- Test rollback: `rails db:rollback` should never crash

## Security
- Use `strong_parameters` — always whitelist in controller, never `permit!`
- Use `bcrypt` (built into Devise) — never MD5/SHA1 for passwords
- Sanitize HTML output with `sanitize` helper — never `html_safe` on user input
- Use `rack-attack` for rate limiting
