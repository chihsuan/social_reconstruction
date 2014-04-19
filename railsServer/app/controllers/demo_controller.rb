class DemoController < ApplicationController
    def index
    end
    def load_json
        @data = File.read("result/data.json")
        return @data
    end
end
