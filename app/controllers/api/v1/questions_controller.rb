class Api::V1::QuestionsController < ApplicationController
  protect_from_forgery with: :null_session

  def create
    question = params[:question]
    shop = params[:store_id]

    return render json: { error: "Missing params" }, status: 400 if question.blank? || shop.blank?

    shop_record = Shop.find_by(shop: shop)
    return render json: { error: "Shop not found" }, status: 404 unless shop_record

    response = Faraday.post(
      ENV["AI_SERVICE_URL"],
      {
        question: question,
        shop: shop,
        access_token: shop_record.access_token
      }.to_json,
      "Content-Type" => "application/json"
    )

    render json: JSON.parse(response.body)
  end
end
