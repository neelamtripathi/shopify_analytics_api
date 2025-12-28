Rails.application.routes.draw do
  namespace :api do
    namespace :v1 do
      post "/questions", to: "questions#create"
    end
  end

  root "home#index"

  get "/auth/shopify", to: "sessions#new"
  get "/auth/shopify/callback", to: "sessions#callback"

  get "up" => "rails/health#show"
end
