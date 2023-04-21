import os
import sys
import pandas as pd
from jinja2 import Environment, FileSystemLoader

script_dir = os.path.dirname(__file__)

# a mapping of column names from the MS Form to names 
# used in the jinja template
col_dict = {
    "ID":"ID",
    "Start time": "Start time",
    "Completion time": "Completion time",
    "Email": "Email",
    "Name": "Name",
    "What's your name?": "your_name",
    "What department do you work in?": "your_department",
    "What would you like the subtitle of your blogpost to be? (Points for festive puns)": "subtitle",
    "What research question are you trying to answer? (The more detail the better)": "research_question",
    "What tools or technologies do you use in your research? (Programming languages, packages, APIs)": "tools_techniques",
    "How does HPC help your research?": "hpc_help",
    "What is the potential impact of your research?": "impact",
    "In your person opinion, what's the coolest thing about your research?": "coolest",
    "Below you're able to upload some images to include in your post. Please use the box below to provide a caption for each image.": "captions",
    "Upload an image/images to be included with your blogpost": "image_file",
    "What's your favourite part of your Christmas dinner?": "christmas_question",
    "Extra content (if there's anything you'd like to add that doesn't fall into the above categories)": "extra_content",
}


def column_mapper(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    A convenience function that maps the col_dict 
    onto the dataframe columns names
    """

    dataframe.columns = dataframe.columns.str.strip().map(col_dict)

    return dataframe


def render_md(content: dict, output_path: str, date: str) -> str:
    """
    A helper function for rendering markdown in jinja2 template

    Loads the 12dayshpc template from the templates directory,
    creates output path to write file too,
    writes file to disk.
    """

    file_loader = FileSystemLoader(os.path.join(script_dir, "templates"))

    env = Environment(loader=file_loader)

    get_template = env.get_template("12dayshpc-template.md.j2")

    post_day = date.split("-")[-1]

    # we have to format the file names like this due to how jekyll
    # expects blogpost file names
    output_file_name = f"{date}-twelvedayshpc2022-Dec{post_day}.md"

    final_path = os.path.join(output_path, output_file_name)

    with open(final_path, "w") as file_todisk:
        file_todisk.write(get_template.render(**content))

    return final_path


def fix_img_paths(data: pd.DataFrame) -> pd.Series:
    """
    A function for fixing image paths generated by Microsoft forms
    """

    assert 'image_file' in data.columns 

    return data['image_file'].fillna("").apply(lambda x: ",".join([x.split("/")[-1].replace("%20","_") for x in  x.split(";")]))


def main(data_file: str, output_path: str, date: str) -> None:
    """
    Main script for loading data in pandas iterating over rows and passing it to render_md
    """
    # open data file from csv
    # expects csv file containing windows encoding from forms
    working_file = pd.read_csv(data_file)

    working_file['image_file'] = fix_img_paths(working_file)

    # fill blank entries (which default to nan)
    # to empty string, we use this in jinja2 template to test for length of variable
    working_file.fillna("", inplace=True)

    # iter through all rows
    for idx, row in working_file.iterrows():

        # render markdown and return filepath it wrote file to
        file_path = render_md(row.to_dict(), output_path, row["Publish_date"])

        # print out to let us know where it wrote too
        print(f"Blog post written to {file_path}")


if __name__ == "__main__":

    # take first command line argument as path to .csv file
    path_to_workbook = sys.argv[1]
    # take 2nd command line argument as output path
    output_path = sys.argv[2]
    # run main on both
    main(path_to_workbook, output_path)
