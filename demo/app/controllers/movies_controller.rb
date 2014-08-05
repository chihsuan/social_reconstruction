class MoviesController < ApplicationController
  def index
  end


  def find_relation
    value = %x(python script/find_relation.py)
  end

  def position_merge
    value = %x(python script/position_merge.py)
    face_recognition
    render :index
  end

  def face_recognition
    value = %x(python script/face_recognition.py)
    role_reconstruct
  end


  def role_reconstruct
    value = %x(python script/role_reconstruct.py)
    social_reconstruction 
  end


  def social_reconstruction
    value = %x(python script/social_reconstruction.py)
  end

  def get_data
    @data = File.read("output/relation_graph.json")
    render :json => @data 
  end

end
