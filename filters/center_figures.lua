-- Filter images with this function if the target format is HTML
if FORMAT:match("html") then
	function Image(elem)
		-- Use CSS style to center image
		elem.attributes.style = "margin:auto; display: block;"
		return elem
	end
end
