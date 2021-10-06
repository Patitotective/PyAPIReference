BACKSLASH = "\\"
def convert_tree_to_markdown(tree: dict):
	def parameters_to_markdown(parameters: dict):
		empty = True
		markdown_text = "#### Parameters\n"
		
		for parameter_name, parameter_props in parameters.items():
			empty = False

			parameter_text = f"`{parameter_name}"

			if parameter_props["annotation"] is not None and parameter_props["default"] is not None:
				parameter_text += f" ({parameter_props['annotation']}={parameter_props['default']})`"
			elif parameter_props["annotation"] is not None and parameter_props["default"] is None:
				parameter_text += f" ({parameter_props['annotation']})`"

			elif parameter_props["default"] is not None:
				parameter_text += f"={parameter_props['default']}`"
			else:
				parameter_text += "`"

			markdown_text += f"- {parameter_text}\n"

		return markdown_text if not empty else None

	def class_to_markdown(class_name: str, class_dict: dict):
		def class_content_to_markdown(content: dict):
			markdown_text = ""

			for member_name, member_props in content.items():
				member_type = member_props["type"]
				member_docstring = member_props["docstring"]

				if member_type == "function":
					member_type = "method"

				if "value" in member_props: # Means it's a variable so the docstring will be a description of the variable type
					member_docstring = None
					markdown_text += f"#### `{class_name}.{member_name} ({member_type}) = {member_props['value']}`\n"
				else:
					markdown_text += f"#### `{class_name}.{member_name} ({member_type})`\n"
				
				markdown_text += f"{member_docstring if member_docstring is not None else f'{member_name} has no description.'}".strip() + "\n\n"

				if "parameters" in member_props:
					parameter_text = parameters_to_markdown(member_props["parameters"])
					markdown_text += parameter_text.strip() + "\n\n" if parameter_text is not None else "" 

				elif member_type == "class":
					class_text = class_to_markdown(member_name, member_props)					
					markdown_text += class_text.strip() + "\n\n" if class_text is not None else "" 

			return markdown_text

		markdown_text = ""

		for property_name, property_val in class_dict.items():
			if property_name == "inherits" and len(property_val) > 0:
				markdown_text += f"Inherits: `{', '.join(property_val)}`.\n"

		markdown_text += class_content_to_markdown(class_dict["content"])

		return markdown_text

	def content_to_markdown(content: dict) -> str:
		"""
		Parameters:
			change_members_type (dict={}): You can pass a dictionary with the key being the type to change for the value.
		Example:
			change_members_type={"function": "method"}
		"""
		markdown_text = ""

		for member_name, member_props in content.items():
			member_type = member_props["type"]
			member_docstring = member_props["docstring"]

			if "value" in member_props: # Means it's a variable so the docstring will be a description of the variable type
				member_docstring = None			
				markdown_text += f"#### `{member_name} ({member_type}) = {member_props['value']}`\n"
			else:
				markdown_text += f"### `{member_name} ({member_type})`\n"
			
			markdown_text += f"{member_docstring if member_docstring is not None else f'{member_name} has no description.'}".strip() + "\n\n"

			if "parameters" in member_props:
				parameter_text = parameters_to_markdown(member_props["parameters"])
				markdown_text += parameter_text.strip() + "\n\n" if parameter_text is not None else "" 

			elif member_type == "class":
				class_text = class_to_markdown(member_name, member_props)					
				markdown_text += class_text.strip() + "\n\n" if class_text is not None else "" 

		return markdown_text

	# print(PREFS.convert_to_prefs(tree))

	# object is the main object on the tree
	module_name = tuple(tree)[0]
	module_content = tree[module_name]

	markdown_text = f"# {module_name}\n"

	for property_name, property_val in module_content.items():
		if isinstance(property_val, dict):
			markdown_text += content_to_markdown(property_val)

		elif property_name == "docstring":
			markdown_text += f"{property_val if property_val is not None else f'{module_name} has no docstring.'}".strip() + "\n\n"
			continue

	markdown_text += "---\n_Created using [PyAPIReference](https://patitotective.github.io/PyAPIReference/)._"

	return markdown_text.strip() + "\n" # This way it only lefts one line at the end
