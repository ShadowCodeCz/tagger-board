import os

import taggerboard
import argparse

taggerboard.app.ApplicationCLI.run(argparse.Namespace(**{
    "configuration": "./debug.configuration.json",
}))

